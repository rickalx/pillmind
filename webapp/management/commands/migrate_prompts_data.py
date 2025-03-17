import json
import uuid
from django.core.management.base import BaseCommand
from django.db import transaction
from webapp.models import AnalisisPropuesta, Prompt

class Command(BaseCommand):
    help = 'Migra datos de prompts_utilizados (JSONField) a prompts (ManyToManyField)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Ejecutar en modo simulación sin realizar cambios',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        if dry_run:
            self.stdout.write(self.style.WARNING('Ejecutando en modo simulación (--dry-run)'))
        
        # Obtener todos los análisis con prompts_utilizados no nulos
        analisis_con_prompts = AnalisisPropuesta.objects.exclude(prompts_utilizados__isnull=True).exclude(prompts_utilizados={})
        
        self.stdout.write(f'Encontrados {analisis_con_prompts.count()} análisis con prompts_utilizados')
        
        # Contador para estadísticas
        stats = {
            'analisis_procesados': 0,
            'prompts_creados': 0,
            'prompts_vinculados': 0,
            'errores': 0
        }
        
        # Procesar cada análisis
        for analisis in analisis_con_prompts:
            try:
                self._procesar_analisis(analisis, dry_run, stats)
            except Exception as e:
                stats['errores'] += 1
                self.stdout.write(self.style.ERROR(f'Error procesando análisis {analisis.id}: {str(e)}'))
        
        # Mostrar estadísticas
        self.stdout.write(self.style.SUCCESS(f'Migración completada:'))
        self.stdout.write(f'  - Análisis procesados: {stats["analisis_procesados"]}')
        self.stdout.write(f'  - Prompts creados: {stats["prompts_creados"]}')
        self.stdout.write(f'  - Prompts vinculados: {stats["prompts_vinculados"]}')
        self.stdout.write(f'  - Errores: {stats["errores"]}')
        
        if dry_run:
            self.stdout.write(self.style.WARNING('Ningún cambio fue realizado (modo simulación)'))
    
    def _procesar_analisis(self, analisis, dry_run, stats):
        """Procesa un análisis individual"""
        prompts_data = analisis.prompts_utilizados
        
        # Verificar formato de datos
        if not isinstance(prompts_data, dict) and not isinstance(prompts_data, list):
            try:
                # Intentar parsear si es una cadena JSON
                if isinstance(prompts_data, str):
                    prompts_data = json.loads(prompts_data)
                else:
                    self.stdout.write(self.style.WARNING(
                        f'Formato no reconocido para análisis {analisis.id}: {type(prompts_data)}'
                    ))
                    return
            except json.JSONDecodeError:
                self.stdout.write(self.style.WARNING(
                    f'JSON inválido en análisis {analisis.id}'
                ))
                return
        
        # Incrementar contador
        stats['analisis_procesados'] += 1
        
        # Diferentes estrategias según el formato de datos
        if isinstance(prompts_data, dict):
            self._procesar_dict_prompts(analisis, prompts_data, dry_run, stats)
        elif isinstance(prompts_data, list):
            self._procesar_list_prompts(analisis, prompts_data, dry_run, stats)
    
    def _procesar_dict_prompts(self, analisis, prompts_data, dry_run, stats):
        """Procesa prompts en formato diccionario"""
        for key, value in prompts_data.items():
            # Crear o encontrar prompt
            prompt_obj = self._crear_o_encontrar_prompt(
                objetivo=key,
                texto=value if isinstance(value, str) else json.dumps(value, ensure_ascii=False),
                dry_run=dry_run,
                stats=stats
            )
            
            if prompt_obj and not dry_run:
                # Vincular prompt al análisis
                analisis.prompts.add(prompt_obj)
                stats['prompts_vinculados'] += 1
    
    def _procesar_list_prompts(self, analisis, prompts_data, dry_run, stats):
        """Procesa prompts en formato lista"""
        for i, item in enumerate(prompts_data):
            if isinstance(item, dict):
                # Si el item es un diccionario, buscar campos conocidos
                objetivo = item.get('objetivo', item.get('title', f'Prompt {i+1}'))
                texto = item.get('texto', item.get('text', item.get('content', json.dumps(item, ensure_ascii=False))))
            else:
                # Si es otro tipo, usar índice como objetivo
                objetivo = f'Prompt {i+1}'
                texto = item if isinstance(item, str) else json.dumps(item, ensure_ascii=False)
            
            # Crear o encontrar prompt
            prompt_obj = self._crear_o_encontrar_prompt(
                objetivo=objetivo,
                texto=texto,
                dry_run=dry_run,
                stats=stats
            )
            
            if prompt_obj and not dry_run:
                # Vincular prompt al análisis
                analisis.prompts.add(prompt_obj)
                stats['prompts_vinculados'] += 1
    
    @transaction.atomic
    def _crear_o_encontrar_prompt(self, objetivo, texto, dry_run, stats):
        """Crea o encuentra un prompt existente"""
        if dry_run:
            # En modo simulación, no crear objetos
            self.stdout.write(f'  [Simulación] Creando prompt: {objetivo[:30]}...')
            return None
        
        # Buscar prompt existente con el mismo texto
        prompt_existente = Prompt.objects.filter(texto=texto).first()
        
        if prompt_existente:
            return prompt_existente
        
        # Crear nuevo prompt
        nuevo_prompt = Prompt(
            id=uuid.uuid4(),
            objetivo=objetivo[:255],  # Limitar a la longitud máxima del campo
            texto=texto,
            version='1.0.0',
            estado=Prompt.Estado.BORRADOR,  # Por defecto, todos los prompts migrados están en borrador
            # No asignamos rol_ia automáticamente ya que requiere revisión manual
        )
        nuevo_prompt.save()
        stats['prompts_creados'] += 1
        
        return nuevo_prompt
