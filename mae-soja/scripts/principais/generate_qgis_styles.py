#!/usr/bin/env python3
"""
Script para gerar arquivos de estilo (.qml) do QGIS para os resultados de segmentação.
"""

import os
import xml.etree.ElementTree as ET
from xml.dom import minidom

def create_segmentation_style():
    """Cria estilo para GeoTIFFs de segmentação (classes)."""
    
    qml_content = '''<?xml version="1.0" encoding="UTF-8"?>
<qgis version="3.22.0" styleCategories="AllStyleCategories">
  <pipe-data-defined-properties>
    <Option type="Map">
      <Option type="QString" value="" name="name"/>
      <Option name="properties"/>
      <Option type="QString" value="collection" name="type"/>
    </Option>
  </pipe-data-defined-properties>
  <pipe>
    <provider>
      <resampling enabled="false" maxOversampling="2" zoomedInResamplingMethod="nearestNeighbour" zoomedOutResamplingMethod="nearestNeighbour"/>
    </provider>
    <rasterrenderer band="1" type="paletted" opacity="1" alphaBand="-1" nodataColor="">
      <rasterTransparency/>
      <minMaxOrigin>
        <limits>None</limits>
        <extent>WholeRaster</extent>
        <statAccuracy>Estimated</statAccuracy>
        <cumulativeCutLower>0.02</cumulativeCutLower>
        <cumulativeCutUpper>0.98</cumulativeCutUpper>
        <stdDevFactor>2</stdDevFactor>
      </minMaxOrigin>
      <colorPalette>
        <paletteEntry alpha="0" color="#ffffff" value="0" label="Background"/>
        <paletteEntry alpha="255" color="#2d5a27" value="1" label="Gramínea Porte Alto"/>
        <paletteEntry alpha="255" color="#7cb342" value="2" label="Gramínea Porte Baixo"/>
        <paletteEntry alpha="255" color="#fdd835" value="3" label="Outras Folhas Largas"/>
        <paletteEntry alpha="255" color="#e53935" value="4" label="Trepadeira"/>
      </colorPalette>
    </rasterrenderer>
    <brightnesscontrast brightness="0" gamma="1" contrast="0"/>
    <huesaturation colorizeGreen="128" colorizeOn="0" colorizeRed="255" colorizeBlue="128" grayscaleMode="0" saturation="0" colorizeStrength="100"/>
    <rasterresampler maxOversampling="2"/>
    <resamplingStage>resamplingFilter</resamplingStage>
  </pipe>
  <blendMode>0</blendMode>
</qgis>'''
    
    return qml_content

def create_shapefile_weed_coverage_style():
    """Cria estilo para shapefile baseado na cobertura de daninhas."""
    
    qml_content = '''<?xml version="1.0" encoding="UTF-8"?>
<qgis version="3.22.0" styleCategories="AllStyleCategories">
  <renderer-v2 type="graduatedSymbol" attr="weed_cover" symbollevels="0" enableorderby="0" forceraster="0" graduatedMethod="GraduatedColor">
    <ranges>
      <range render="true" symbol="0" lower="0.000000" upper="5.000000" label="0.0 - 5.0% (Baixa)"/>
      <range render="true" symbol="1" lower="5.000000" upper="15.000000" label="5.0 - 15.0% (Moderada)"/>
      <range render="true" symbol="2" lower="15.000000" upper="30.000000" label="15.0 - 30.0% (Alta)"/>
      <range render="true" symbol="3" lower="30.000000" upper="100.000000" label="30.0 - 100.0% (Muito Alta)"/>
    </ranges>
    <symbols>
      <symbol type="fill" name="0" alpha="1" clip_to_extent="1">
        <data_defined_properties>
          <Option type="Map">
            <Option type="QString" value="" name="name"/>
            <Option name="properties"/>
            <Option type="QString" value="collection" name="type"/>
          </Option>
        </data_defined_properties>
        <layer enabled="1" class="SimpleFill" locked="0" pass="0">
          <Option type="Map">
            <Option type="QString" value="3x:0,0,0,0,0,0" name="border_width_map_unit_scale"/>
            <Option type="QString" value="255,255,255,0" name="color"/>
            <Option type="QString" value="bevel" name="joinstyle"/>
            <Option type="QString" value="0,0" name="offset"/>
            <Option type="QString" value="3x:0,0,0,0,0,0" name="offset_map_unit_scale"/>
            <Option type="QString" value="MM" name="offset_unit"/>
            <Option type="QString" value="#4caf50" name="outline_color"/>
            <Option type="QString" value="solid" name="outline_style"/>
            <Option type="QString" value="2" name="outline_width"/>
            <Option type="QString" value="MM" name="outline_width_unit"/>
            <Option type="QString" value="no" name="style"/>
          </Option>
        </layer>
      </symbol>
      <symbol type="fill" name="1" alpha="1" clip_to_extent="1">
        <data_defined_properties>
          <Option type="Map">
            <Option type="QString" value="" name="name"/>
            <Option name="properties"/>
            <Option type="QString" value="collection" name="type"/>
          </Option>
        </data_defined_properties>
        <layer enabled="1" class="SimpleFill" locked="0" pass="0">
          <Option type="Map">
            <Option type="QString" value="3x:0,0,0,0,0,0" name="border_width_map_unit_scale"/>
            <Option type="QString" value="255,255,255,0" name="color"/>
            <Option type="QString" value="bevel" name="joinstyle"/>
            <Option type="QString" value="0,0" name="offset"/>
            <Option type="QString" value="3x:0,0,0,0,0,0" name="offset_map_unit_scale"/>
            <Option type="QString" value="MM" name="offset_unit"/>
            <Option type="QString" value="#ffeb3b" name="outline_color"/>
            <Option type="QString" value="solid" name="outline_style"/>
            <Option type="QString" value="2" name="outline_width"/>
            <Option type="QString" value="MM" name="outline_width_unit"/>
            <Option type="QString" value="no" name="style"/>
          </Option>
        </layer>
      </symbol>
      <symbol type="fill" name="2" alpha="1" clip_to_extent="1">
        <data_defined_properties>
          <Option type="Map">
            <Option type="QString" value="" name="name"/>
            <Option name="properties"/>
            <Option type="QString" value="collection" name="type"/>
          </Option>
        </data_defined_properties>
        <layer enabled="1" class="SimpleFill" locked="0" pass="0">
          <Option type="Map">
            <Option type="QString" value="3x:0,0,0,0,0,0" name="border_width_map_unit_scale"/>
            <Option type="QString" value="255,255,255,0" name="color"/>
            <Option type="QString" value="bevel" name="joinstyle"/>
            <Option type="QString" value="0,0" name="offset"/>
            <Option type="QString" value="3x:0,0,0,0,0,0" name="offset_map_unit_scale"/>
            <Option type="QString" value="MM" name="offset_unit"/>
            <Option type="QString" value="#ff9800" name="outline_color"/>
            <Option type="QString" value="solid" name="outline_style"/>
            <Option type="QString" value="2" name="outline_width"/>
            <Option type="QString" value="MM" name="outline_width_unit"/>
            <Option type="QString" value="no" name="style"/>
          </Option>
        </layer>
      </symbol>
      <symbol type="fill" name="3" alpha="1" clip_to_extent="1">
        <data_defined_properties>
          <Option type="Map">
            <Option type="QString" value="" name="name"/>
            <Option name="properties"/>
            <Option type="QString" value="collection" name="type"/>
          </Option>
        </data_defined_properties>
        <layer enabled="1" class="SimpleFill" locked="0" pass="0">
          <Option type="Map">
            <Option type="QString" value="3x:0,0,0,0,0,0" name="border_width_map_unit_scale"/>
            <Option type="QString" value="255,255,255,0" name="color"/>
            <Option type="QString" value="bevel" name="joinstyle"/>
            <Option type="QString" value="0,0" name="offset"/>
            <Option type="QString" value="3x:0,0,0,0,0,0" name="offset_map_unit_scale"/>
            <Option type="QString" value="MM" name="offset_unit"/>
            <Option type="QString" value="#f44336" name="outline_color"/>
            <Option type="QString" value="solid" name="outline_style"/>
            <Option type="QString" value="2" name="outline_width"/>
            <Option type="QString" value="MM" name="outline_width_unit"/>
            <Option type="QString" value="no" name="style"/>
          </Option>
        </layer>
      </symbol>
    </symbols>
    <source-symbol>
      <symbol type="fill" name="0" alpha="1" clip_to_extent="1">
        <data_defined_properties>
          <Option type="Map">
            <Option type="QString" value="" name="name"/>
            <Option name="properties"/>
            <Option type="QString" value="collection" name="type"/>
          </Option>
        </data_defined_properties>
        <layer enabled="1" class="SimpleFill" locked="0" pass="0">
          <Option type="Map">
            <Option type="QString" value="3x:0,0,0,0,0,0" name="border_width_map_unit_scale"/>
            <Option type="QString" value="152,125,183,255" name="color"/>
            <Option type="QString" value="bevel" name="joinstyle"/>
            <Option type="QString" value="0,0" name="offset"/>
            <Option type="QString" value="3x:0,0,0,0,0,0" name="offset_map_unit_scale"/>
            <Option type="QString" value="MM" name="offset_unit"/>
            <Option type="QString" value="35,35,35,255" name="outline_color"/>
            <Option type="QString" value="solid" name="outline_style"/>
            <Option type="QString" value="0.26" name="outline_width"/>
            <Option type="QString" value="MM" name="outline_width_unit"/>
            <Option type="QString" value="solid" name="style"/>
          </Option>
        </layer>
      </symbol>
    </source-symbol>
    <mode name="EqualInterval"/>
    <labelformat format=" %1 - %2 " precision="1" trimtrailingzeroes="false"/>
  </renderer-v2>
  <blendMode>0</blendMode>
</qgis>'''
    
    return qml_content

def create_shapefile_outline_only_style():
    """Cria estilo para shapefile com apenas contorno (sem preenchimento)."""
    
    qml_content = '''<?xml version="1.0" encoding="UTF-8"?>
<qgis version="3.22.0" styleCategories="AllStyleCategories">
  <renderer-v2 type="singleSymbol" symbollevels="0" enableorderby="0" forceraster="0">
    <symbols>
      <symbol type="fill" name="0" alpha="1" clip_to_extent="1">
        <data_defined_properties>
          <Option type="Map">
            <Option type="QString" value="" name="name"/>
            <Option name="properties"/>
            <Option type="QString" value="collection" name="type"/>
          </Option>
        </data_defined_properties>
        <layer enabled="1" class="SimpleFill" locked="0" pass="0">
          <Option type="Map">
            <Option type="QString" value="3x:0,0,0,0,0,0" name="border_width_map_unit_scale"/>
            <Option type="QString" value="255,255,255,0" name="color"/>
            <Option type="QString" value="bevel" name="joinstyle"/>
            <Option type="QString" value="0,0" name="offset"/>
            <Option type="QString" value="3x:0,0,0,0,0,0" name="offset_map_unit_scale"/>
            <Option type="QString" value="MM" name="offset_unit"/>
            <Option type="QString" value="#e74c3c" name="outline_color"/>
            <Option type="QString" value="solid" name="outline_style"/>
            <Option type="QString" value="2" name="outline_width"/>
            <Option type="QString" value="MM" name="outline_width_unit"/>
            <Option type="QString" value="no" name="style"/>
          </Option>
        </layer>
      </symbol>
    </symbols>
    <rotation/>
    <sizescale/>
  </renderer-v2>
  <blendMode>0</blendMode>
</qgis>'''
    
    return qml_content

def create_shapefile_outline_by_weed_type_style():
    """Cria estilo para shapefile com contorno colorido por tipo de daninha dominante."""
    
    qml_content = '''<?xml version="1.0" encoding="UTF-8"?>
<qgis version="3.22.0" styleCategories="AllStyleCategories">
  <renderer-v2 type="categorizedSymbol" attr="dom_weed" symbollevels="0" enableorderby="0" forceraster="0">
    <categories>
      <category render="true" symbol="0" value="" label="Sem Daninhas"/>
      <category render="true" symbol="1" value="Graminea P" label="Gramínea Porte Alto"/>
      <category render="true" symbol="2" value="Graminea P" label="Gramínea Porte Baixo"/>
      <category render="true" symbol="3" value="Outras Fol" label="Outras Folhas Largas"/>
      <category render="true" symbol="4" value="Trepadeira" label="Trepadeira"/>
    </categories>
    <symbols>
      <symbol type="fill" name="0" alpha="1" clip_to_extent="1">
        <layer enabled="1" class="SimpleFill" locked="0" pass="0">
          <Option type="Map">
            <Option type="QString" value="255,255,255,0" name="color"/>
            <Option type="QString" value="#cccccc" name="outline_color"/>
            <Option type="QString" value="dash" name="outline_style"/>
            <Option type="QString" value="1" name="outline_width"/>
            <Option type="QString" value="no" name="style"/>
          </Option>
        </layer>
      </symbol>
      <symbol type="fill" name="1" alpha="1" clip_to_extent="1">
        <layer enabled="1" class="SimpleFill" locked="0" pass="0">
          <Option type="Map">
            <Option type="QString" value="255,255,255,0" name="color"/>
            <Option type="QString" value="#2d5a27" name="outline_color"/>
            <Option type="QString" value="solid" name="outline_style"/>
            <Option type="QString" value="2.5" name="outline_width"/>
            <Option type="QString" value="no" name="style"/>
          </Option>
        </layer>
      </symbol>
      <symbol type="fill" name="2" alpha="1" clip_to_extent="1">
        <layer enabled="1" class="SimpleFill" locked="0" pass="0">
          <Option type="Map">
            <Option type="QString" value="255,255,255,0" name="color"/>
            <Option type="QString" value="#7cb342" name="outline_color"/>
            <Option type="QString" value="solid" name="outline_style"/>
            <Option type="QString" value="2.5" name="outline_width"/>
            <Option type="QString" value="no" name="style"/>
          </Option>
        </layer>
      </symbol>
      <symbol type="fill" name="3" alpha="1" clip_to_extent="1">
        <layer enabled="1" class="SimpleFill" locked="0" pass="0">
          <Option type="Map">
            <Option type="QString" value="255,255,255,0" name="color"/>
            <Option type="QString" value="#fdd835" name="outline_color"/>
            <Option type="QString" value="solid" name="outline_style"/>
            <Option type="QString" value="2.5" name="outline_width"/>
            <Option type="QString" value="no" name="style"/>
          </Option>
        </layer>
      </symbol>
      <symbol type="fill" name="4" alpha="1" clip_to_extent="1">
        <layer enabled="1" class="SimpleFill" locked="0" pass="0">
          <Option type="Map">
            <Option type="QString" value="255,255,255,0" name="color"/>
            <Option type="QString" value="#e53935" name="outline_color"/>
            <Option type="QString" value="solid" name="outline_style"/>
            <Option type="QString" value="2.5" name="outline_width"/>
            <Option type="QString" value="no" name="style"/>
          </Option>
        </layer>
      </symbol>
    </symbols>
  </renderer-v2>
  <blendMode>0</blendMode>
</qgis>'''
    
    return qml_content

def generate_styles_for_directory(results_dir, style_type='outline'):
    """Gera arquivos de estilo para todos os resultados em um diretório."""
    
    if not os.path.exists(results_dir):
        print(f"❌ Diretório não encontrado: {results_dir}")
        return
    
    # Estilo para GeoTIFFs de segmentação (sempre o mesmo)
    segmentation_style = create_segmentation_style()
    
    # Escolhe o estilo para shapefile baseado no tipo
    if style_type == 'filled':
        shapefile_style = create_shapefile_weed_coverage_style()
        style_suffix = ''  # Arquivo padrão .qml
    elif style_type == 'outline':
        shapefile_style = create_shapefile_outline_only_style()
        style_suffix = '_outline'
    elif style_type == 'outline_by_type':
        shapefile_style = create_shapefile_outline_by_weed_type_style()
        style_suffix = '_outline_by_type'
    else:
        print(f"❌ Tipo de estilo não reconhecido: {style_type}")
        return
    
    files_processed = 0
    
    # Processa todos os arquivos no diretório
    for file in os.listdir(results_dir):
        file_path = os.path.join(results_dir, file)
        
        # Para GeoTIFFs de segmentação (sempre gera o mesmo estilo)
        if file.endswith('_segmentation.tif') and style_type == 'filled':
            qml_path = file_path.replace('.tif', '.qml')
            with open(qml_path, 'w', encoding='utf-8') as f:
                f.write(segmentation_style)
            print(f"   ✓ Estilo raster: {os.path.basename(qml_path)}")
            files_processed += 1
        
        # Para shapefiles de resultados
        elif file.endswith('_resultados.shp'):
            if style_suffix:
                qml_path = file_path.replace('.shp', f'{style_suffix}.qml')
            else:
                qml_path = file_path.replace('.shp', '.qml')
                
            with open(qml_path, 'w', encoding='utf-8') as f:
                f.write(shapefile_style)
            print(f"   ✓ Estilo shapefile: {os.path.basename(qml_path)}")
            files_processed += 1
    
    if files_processed > 0:
        print(f"   📊 Arquivos processados: {files_processed}")
    else:
        print(f"   ⚠️  Nenhum arquivo encontrado para processar")

def main():
    """Função principal."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Gera arquivos de estilo QGIS (.qml)')
    parser.add_argument('--dir', type=str, 
                       default='/home/lades/computer_vision/wesley/mae-soja/data/output/resultados_segmentacao_talhoes',
                       help='Diretório com os resultados')
    parser.add_argument('--area', type=str, help='Área específica para processar estilos')
    parser.add_argument('--style', type=str, choices=['filled', 'outline', 'outline_by_type', 'all'],
                       default='outline', help='Tipo de estilo: filled (preenchido), outline (só contorno), outline_by_type (contorno por tipo), all (todos os estilos)')
    
    args = parser.parse_args()
    
    print(f"🎨 GERADOR DE ESTILOS QGIS")
    print(f"📋 Tipo de estilo selecionado: {args.style}")
    print(f"" + "="*50)
    
    # Gera estilos específicos ou todos
    styles_to_generate = []
    if args.style == 'all':
        styles_to_generate = ['filled', 'outline', 'outline_by_type']
    else:
        styles_to_generate = [args.style]
    
    if args.area:
        # Processa área específica
        area_dir = os.path.join(args.dir, args.area)
        for style_type in styles_to_generate:
            print(f"\n🎯 Gerando estilo '{style_type}' para área: {args.area}")
            generate_styles_for_directory(area_dir, style_type)
    else:
        # Processa todas as áreas
        if os.path.exists(args.dir):
            areas = [d for d in os.listdir(args.dir) if os.path.isdir(os.path.join(args.dir, d))]
            print(f"📂 Total de áreas encontradas: {len(areas)}")
            
            for area in areas:
                area_path = os.path.join(args.dir, area)
                for style_type in styles_to_generate:
                    print(f"\n🎯 Gerando estilo '{style_type}' para área: {area}")
                    generate_styles_for_directory(area_path, style_type)
        else:
            print(f"❌ Diretório não encontrado: {args.dir}")
    
    print(f"\n🎉 PROCESSO CONCLUÍDO!")
    print(f"📋 Instruções de uso no QGIS:")
    print(f"   1. Carregue o shapefile no QGIS")
    print(f"   2. Botão direito → Propriedades → Simbologia")
    print(f"   3. Carregar estilo → Selecione arquivo .qml correspondente:")
    for style in styles_to_generate:
        if style == 'filled':
            print(f"      • *_resultados.qml - Estilo preenchido por cobertura")
        elif style == 'outline':
            print(f"      • *_outline.qml - Apenas contorno simples")
        elif style == 'outline_by_type':
            print(f"      • *_outline_by_type.qml - Contorno colorido por tipo")

if __name__ == "__main__":
    main()
