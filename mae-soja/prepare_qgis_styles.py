#!/usr/bin/env python3
"""
Script de demonstração para visualizar resultados da segmentação por talhões no QGIS.
Este script gera arquivos QML (estilos) para facilitar a visualização dos resultados.
"""

import os
from pathlib import Path
import json

def create_segmentation_style():
    """Cria arquivo QML para estilizar as segmentações no QGIS."""
    
    qml_content = """<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
<qgis version="3.22.0" styleCategories="AllStyleCategories">
  <pipe-data-defined-properties>
    <Option type="Map">
      <Option name="name" type="QString" value=""/>
      <Option name="properties"/>
      <Option name="type" type="QString" value="collection"/>
    </Option>
  </pipe-data-defined-properties>
  <pipe>
    <provider>
      <resampling enabled="false" maxOversampling="2" zoomedInResamplingMethod="nearestNeighbour" zoomedOutResamplingMethod="nearestNeighbour"/>
    </provider>
    <rasterrenderer alphaBand="-1" band="1" classificationMax="4" classificationMin="0" opacity="1" type="singlebandpseudocolor">
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
        <paletteEntry alpha="255" color="#787878" label="Background" value="0"/>
        <paletteEntry alpha="255" color="#ff0000" label="Gramínea Porte Alto" value="1"/>
        <paletteEntry alpha="255" color="#00ff00" label="Gramínea Porte Baixo" value="2"/>
        <paletteEntry alpha="255" color="#0000ff" label="Outras Folhas Largas" value="3"/>
        <paletteEntry alpha="255" color="#00ffff" label="Trepadeira" value="4"/>
      </colorPalette>
      <colorramp name="[source]" type="randomcolors">
        <Option/>
      </colorramp>
    </rasterrenderer>
    <brightnesscontrast brightness="0" contrast="0" gamma="1"/>
    <huesaturation colorizeBlue="128" colorizeGreen="128" colorizeOn="0" colorizeRed="255" colorizeStrength="100" grayscaleMode="0" saturation="0"/>
    <rasterresampler maxOversampling="2"/>
    <resamplingStage>resamplingFilter</resamplingStage>
  </pipe>
  <blendMode>0</blendMode>
</qgis>"""
    
    return qml_content

def create_shapefile_style():
    """Cria arquivo QML para estilizar o shapefile de talhões no QGIS."""
    
    qml_content = """<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
<qgis version="3.22.0" styleCategories="AllStyleCategories">
  <renderer-v2 forceraster="0" type="graduatedSymbol" symbollevels="0" enableorderby="0" graduatedMethod="GraduatedColor" attr="area_seg_h">
    <ranges>
      <range render="true" symbol="0" lower="0.000000000000000" upper="5.000000000000000" label="0.0 - 5.0 ha"/>
      <range render="true" symbol="1" lower="5.000000000000000" upper="15.000000000000000" label="5.0 - 15.0 ha"/>
      <range render="true" symbol="2" lower="15.000000000000000" upper="30.000000000000000" label="15.0 - 30.0 ha"/>
      <range render="true" symbol="3" lower="30.000000000000000" upper="50.000000000000000" label="30.0 - 50.0 ha"/>
    </ranges>
    <symbols>
      <symbol type="fill" name="0" force_rhr="0" alpha="1" clip_to_extent="1">
        <data_defined_properties>
          <Option type="Map">
            <Option type="QString" name="name" value=""/>
            <Option name="properties"/>
            <Option type="QString" name="type" value="collection"/>
          </Option>
        </data_defined_properties>
        <layer enabled="1" class="SimpleFill" locked="0" pass="0">
          <Option type="Map">
            <Option type="QString" name="border_width_map_unit_scale" value="3x:0,0,0,0,0,0"/>
            <Option type="QString" name="color" value="255,245,240,255"/>
            <Option type="QString" name="joinstyle" value="bevel"/>
            <Option type="QString" name="offset" value="0,0"/>
            <Option type="QString" name="offset_map_unit_scale" value="3x:0,0,0,0,0,0"/>
            <Option type="QString" name="offset_unit" value="MM"/>
            <Option type="QString" name="outline_color" value="35,35,35,255"/>
            <Option type="QString" name="outline_style" value="solid"/>
            <Option type="QString" name="outline_width" value="0.26"/>
            <Option type="QString" name="outline_width_unit" value="MM"/>
            <Option type="QString" name="style" value="solid"/>
          </Option>
        </layer>
      </symbol>
      <symbol type="fill" name="1" force_rhr="0" alpha="1" clip_to_extent="1">
        <data_defined_properties>
          <Option type="Map">
            <Option type="QString" name="name" value=""/>
            <Option name="properties"/>
            <Option type="QString" name="type" value="collection"/>
          </Option>
        </data_defined_properties>
        <layer enabled="1" class="SimpleFill" locked="0" pass="0">
          <Option type="Map">
            <Option type="QString" name="border_width_map_unit_scale" value="3x:0,0,0,0,0,0"/>
            <Option type="QString" name="color" value="252,187,161,255"/>
            <Option type="QString" name="joinstyle" value="bevel"/>
            <Option type="QString" name="offset" value="0,0"/>
            <Option type="QString" name="offset_map_unit_scale" value="3x:0,0,0,0,0,0"/>
            <Option type="QString" name="offset_unit" value="MM"/>
            <Option type="QString" name="outline_color" value="35,35,35,255"/>
            <Option type="QString" name="outline_style" value="solid"/>
            <Option type="QString" name="outline_width" value="0.26"/>
            <Option type="QString" name="outline_width_unit" value="MM"/>
            <Option type="QString" name="style" value="solid"/>
          </Option>
        </layer>
      </symbol>
      <symbol type="fill" name="2" force_rhr="0" alpha="1" clip_to_extent="1">
        <data_defined_properties>
          <Option type="Map">
            <Option type="QString" name="name" value=""/>
            <Option name="properties"/>
            <Option type="QString" name="type" value="collection"/>
          </Option>
        </data_defined_properties>
        <layer enabled="1" class="SimpleFill" locked="0" pass="0">
          <Option type="Map">
            <Option type="QString" name="border_width_map_unit_scale" value="3x:0,0,0,0,0,0"/>
            <Option type="QString" name="color" value="251,106,74,255"/>
            <Option type="QString" name="joinstyle" value="bevel"/>
            <Option type="QString" name="offset" value="0,0"/>
            <Option type="QString" name="offset_map_unit_scale" value="3x:0,0,0,0,0,0"/>
            <Option type="QString" name="offset_unit" value="MM"/>
            <Option type="QString" name="outline_color" value="35,35,35,255"/>
            <Option type="QString" name="outline_style" value="solid"/>
            <Option type="QString" name="outline_width" value="0.26"/>
            <Option type="QString" name="outline_width_unit" value="MM"/>
            <Option type="QString" name="style" value="solid"/>
          </Option>
        </layer>
      </symbol>
      <symbol type="fill" name="3" force_rhr="0" alpha="1" clip_to_extent="1">
        <data_defined_properties>
          <Option type="Map">
            <Option type="QString" name="name" value=""/>
            <Option name="properties"/>
            <Option type="QString" name="type" value="collection"/>
          </Option>
        </data_defined_properties>
        <layer enabled="1" class="SimpleFill" locked="0" pass="0">
          <Option type="Map">
            <Option type="QString" name="border_width_map_unit_scale" value="3x:0,0,0,0,0,0"/>
            <Option type="QString" name="color" value="222,45,38,255"/>
            <Option type="QString" name="joinstyle" value="bevel"/>
            <Option type="QString" name="offset" value="0,0"/>
            <Option type="QString" name="offset_map_unit_scale" value="3x:0,0,0,0,0,0"/>
            <Option type="QString" name="offset_unit" value="MM"/>
            <Option type="QString" name="outline_color" value="35,35,35,255"/>
            <Option type="QString" name="outline_style" value="solid"/>
            <Option type="QString" name="outline_width" value="0.26"/>
            <Option type="QString" name="outline_width_unit" value="MM"/>
            <Option type="QString" name="style" value="solid"/>
          </Option>
        </layer>
      </symbol>
    </symbols>
    <source-symbol>
      <symbol type="fill" name="0" force_rhr="0" alpha="1" clip_to_extent="1">
        <data_defined_properties>
          <Option type="Map">
            <Option type="QString" name="name" value=""/>
            <Option name="properties"/>
            <Option type="QString" name="type" value="collection"/>
          </Option>
        </data_defined_properties>
        <layer enabled="1" class="SimpleFill" locked="0" pass="0">
          <Option type="Map">
            <Option type="QString" name="border_width_map_unit_scale" value="3x:0,0,0,0,0,0"/>
            <Option type="QString" name="color" value="152,125,183,255"/>
            <Option type="QString" name="joinstyle" value="bevel"/>
            <Option type="QString" name="offset" value="0,0"/>
            <Option type="QString" name="offset_map_unit_scale" value="3x:0,0,0,0,0,0"/>
            <Option type="QString" name="offset_unit" value="MM"/>
            <Option type="QString" name="outline_color" value="35,35,35,255"/>
            <Option type="QString" name="outline_style" value="solid"/>
            <Option type="QString" name="outline_width" value="0.26"/>
            <Option type="QString" name="outline_width_unit" value="MM"/>
            <Option type="QString" name="style" value="solid"/>
          </Option>
        </layer>
      </symbol>
    </source-symbol>
    <colorramp type="gradient" name="[source]">
      <Option type="Map">
        <Option type="QString" name="color1" value="255,245,240,255"/>
        <Option type="QString" name="color2" value="103,0,13,255"/>
        <Option type="QString" name="discrete" value="0"/>
        <Option type="QString" name="rampType" value="gradient"/>
        <Option type="QString" name="stops" value="0.13;254,224,210,255:0.26;252,187,161,255:0.39;252,146,114,255:0.52;251,106,74,255:0.65;239,59,44,255:0.78;203,24,29,255:0.9;165,15,21,255"/>
      </Option>
    </colorramp>
    <classificationMethod id="Quantile">
      <symmetricMode enabled="0" symmetrypoint="0" astride="0"/>
      <labelFormat format="%1 - %2 ha" labelprecision="1" trimtrailingzeroes="1"/>
      <parameters>
        <Option/>
      </parameters>
      <extraInformation/>
    </classificationMethod>
    <rotation/>
    <sizescale/>
  </renderer-v2>
  <labeling type="simple">
    <settings calloutType="simple">
      <text-style fontItalic="0" fontFamily="Ubuntu" multilineHeight="1" fontSize="10" textOpacity="1" fontWordSpacing="0" fontKerning="1" fontSizeUnit="Point" useSubstitutions="0" fontLetterSpacing="0" namedStyle="Regular" fontWeight="50" textColor="50,50,50,255" textOrientation="horizontal" blendMode="0" fontUnderline="0" fontStrikeout="0" isExpression="0" allowHtml="0" fontSizeMapUnitScale="3x:0,0,0,0,0,0" previewBkgrdColor="255,255,255,255" capitalization="0" fieldName="talhao_id">
        <families/>
        <text-buffer bufferColor="250,250,250,255" bufferBlendMode="0" bufferSize="1" bufferSizeUnits="MM" bufferOpacity="1" bufferNoFill="1" bufferJoinStyle="128" bufferDraw="0" bufferSizeMapUnitScale="3x:0,0,0,0,0,0"/>
        <text-mask maskSize="1.5" maskType="0" maskSizeUnits="MM" maskOpacity="1" maskJoinStyle="128" maskEnabled="0" maskedSymbolLayers="" maskSizeMapUnitScale="3x:0,0,0,0,0,0"/>
        <background shapeRadiiMapUnitScale="3x:0,0,0,0,0,0" shapeSVGFile="" shapeOpacity="1" shapeRadiiX="0" shapeRadiiY="0" shapeSizeX="0" shapeRotationType="0" shapeOffsetMapUnitScale="3x:0,0,0,0,0,0" shapeBlendMode="0" shapeOffsetY="0" shapeSizeY="0" shapeType="0" shapeBorderWidthMapUnitScale="3x:0,0,0,0,0,0" shapeBorderColor="128,128,128,255" shapeJoinStyle="64" shapeRotation="0" shapeRadiiUnit="Point" shapeSizeType="0" shapeDraw="0" shapeBorderWidth="0" shapeSizeMapUnitScale="3x:0,0,0,0,0,0" shapeOffsetX="0" shapeFillColor="255,255,255,255" shapeBorderWidthUnit="Point" shapeSizeUnit="Point" shapeOffsetUnit="Point"/>
        <shadow shadowColor="0,0,0,255" shadowOffsetAngle="135" shadowOffsetGlobal="1" shadowRadiusAlphaOnly="0" shadowUnder="0" shadowOffsetMapUnitScale="3x:0,0,0,0,0,0" shadowRadius="1.5" shadowOffsetDist="1" shadowScale="100" shadowDraw="0" shadowRadiusMapUnitScale="3x:0,0,0,0,0,0" shadowBlendMode="6" shadowOffsetUnit="MM" shadowRadiusUnit="MM" shadowOpacity="0.69999999999999996"/>
        <dd_properties>
          <Option type="Map">
            <Option type="QString" name="name" value=""/>
            <Option name="properties"/>
            <Option type="QString" name="type" value="collection"/>
          </Option>
        </dd_properties>
        <substitutions/>
      </text-style>
      <text-format autoWrapLength="0" multilineAlign="3" formatNumbers="0" wrapChar="" addDirectionSymbol="0" leftDirectionSymbol="&lt;" reverseDirectionSymbol="0" rightDirectionSymbol=">" placeDirectionSymbol="0" decimals="3" useMaxLineLengthForAutoWrap="1" plussign="0"/>
      <placement maxCurvedCharAngleOut="-25" layerType="PolygonGeometry" lineAnchorClipping="0" repeatDistanceMapUnitScale="3x:0,0,0,0,0,0" centroidWhole="0" predefinedPositionOrder="TR,TL,BR,BL,R,L,TSR,BSR" repeatDistanceUnits="MM" overrunDistanceMapUnitScale="3x:0,0,0,0,0,0" xOffset="0" polygonPlacementFlags="2" lineAnchorPercent="0.5" lineAnchorType="0" quadOffset="4" yOffset="0" distMapUnitScale="3x:0,0,0,0,0,0" centroidInside="0" priority="5" maxCurvedCharAngleIn="25" preserveRotation="1" rotationAngle="0" offsetUnits="MM" geometryGeneratorType="PointGeometry" rotationUnit="AngleDegrees" offsetType="0" placement="0" placementFlags="10" dist="0" fitInPolygonOnly="0" overrunDistance="0" distUnits="MM" repeatDistance="0" geometryGenerator="" geometryGeneratorEnabled="0"/>
      <rendering mergeLines="0" limitNumLabels="0" fontLimitPixelSize="0" displayAll="0" labelPerPart="0" fontMaxPixelSize="10000" obstacle="1" obstacleFactor="1" fontMinPixelSize="3" scaleVisibility="0" maxNumLabels="2000" zIndex="0" minFeatureSize="0" obstacleType="1" scaleMin="0" scaleMax="0" drawLabels="1" upsidedownLabels="0"/>
      <dd_properties>
        <Option type="Map">
          <Option type="QString" name="name" value=""/>
          <Option name="properties"/>
          <Option type="QString" name="type" value="collection"/>
        </Option>
      </dd_properties>
      <callout type="simple">
        <Option type="Map">
          <Option type="QString" name="anchorPoint" value="pole_of_inaccessibility"/>
          <Option type="Map" name="ddProperties">
            <Option type="QString" name="name" value=""/>
            <Option name="properties"/>
            <Option type="QString" name="type" value="collection"/>
          </Option>
          <Option type="bool" name="drawToAllParts" value="false"/>
          <Option type="QString" name="enabled" value="0"/>
          <Option type="QString" name="labelAnchorPoint" value="point_on_exterior"/>
          <Option type="QString" name="lineSymbol" value="&lt;symbol type=&quot;line&quot; name=&quot;symbol&quot; force_rhr=&quot;0&quot; alpha=&quot;1&quot; clip_to_extent=&quot;1&quot;>&lt;data_defined_properties>&lt;Option type=&quot;Map&quot;>&lt;Option type=&quot;QString&quot; name=&quot;name&quot; value=&quot;&quot;/>&lt;Option name=&quot;properties&quot;/>&lt;Option type=&quot;QString&quot; name=&quot;type&quot; value=&quot;collection&quot;/>&lt;/Option>&lt;/data_defined_properties>&lt;layer enabled=&quot;1&quot; class=&quot;SimpleLine&quot; locked=&quot;0&quot; pass=&quot;0&quot;>&lt;Option type=&quot;Map&quot;>&lt;Option type=&quot;QString&quot; name=&quot;align_dash_pattern&quot; value=&quot;0&quot;/>&lt;Option type=&quot;QString&quot; name=&quot;capstyle&quot; value=&quot;square&quot;/>&lt;Option type=&quot;QString&quot; name=&quot;customdash&quot; value=&quot;5;2&quot;/>&lt;Option type=&quot;QString&quot; name=&quot;customdash_map_unit_scale&quot; value=&quot;3x:0,0,0,0,0,0&quot;/>&lt;Option type=&quot;QString&quot; name=&quot;customdash_unit&quot; value=&quot;MM&quot;/>&lt;Option type=&quot;QString&quot; name=&quot;dash_pattern_offset&quot; value=&quot;0&quot;/>&lt;Option type=&quot;QString&quot; name=&quot;dash_pattern_offset_map_unit_scale&quot; value=&quot;3x:0,0,0,0,0,0&quot;/>&lt;Option type=&quot;QString&quot; name=&quot;dash_pattern_offset_unit&quot; value=&quot;MM&quot;/>&lt;Option type=&quot;QString&quot; name=&quot;draw_inside_polygon&quot; value=&quot;0&quot;/>&lt;Option type=&quot;QString&quot; name=&quot;joinstyle&quot; value=&quot;bevel&quot;/>&lt;Option type=&quot;QString&quot; name=&quot;line_color&quot; value=&quot;60,60,60,255&quot;/>&lt;Option type=&quot;QString&quot; name=&quot;line_style&quot; value=&quot;solid&quot;/>&lt;Option type=&quot;QString&quot; name=&quot;line_width&quot; value=&quot;0.3&quot;/>&lt;Option type=&quot;QString&quot; name=&quot;line_width_unit&quot; value=&quot;MM&quot;/>&lt;Option type=&quot;QString&quot; name=&quot;offset&quot; value=&quot;0&quot;/>&lt;Option type=&quot;QString&quot; name=&quot;offset_map_unit_scale&quot; value=&quot;3x:0,0,0,0,0,0&quot;/>&lt;Option type=&quot;QString&quot; name=&quot;offset_unit&quot; value=&quot;MM&quot;/>&lt;Option type=&quot;QString&quot; name=&quot;ring_filter&quot; value=&quot;0&quot;/>&lt;Option type=&quot;QString&quot; name=&quot;trim_distance_end&quot; value=&quot;0&quot;/>&lt;Option type=&quot;QString&quot; name=&quot;trim_distance_end_map_unit_scale&quot; value=&quot;3x:0,0,0,0,0,0&quot;/>&lt;Option type=&quot;QString&quot; name=&quot;trim_distance_end_unit&quot; value=&quot;MM&quot;/>&lt;Option type=&quot;QString&quot; name=&quot;trim_distance_start&quot; value=&quot;0&quot;/>&lt;Option type=&quot;QString&quot; name=&quot;trim_distance_start_map_unit_scale&quot; value=&quot;3x:0,0,0,0,0,0&quot;/>&lt;Option type=&quot;QString&quot; name=&quot;trim_distance_start_unit&quot; value=&quot;MM&quot;/>&lt;Option type=&quot;QString&quot; name=&quot;tweak_dash_pattern_on_corners&quot; value=&quot;0&quot;/>&lt;Option type=&quot;QString&quot; name=&quot;use_custom_dash&quot; value=&quot;0&quot;/>&lt;Option type=&quot;QString&quot; name=&quot;width_map_unit_scale&quot; value=&quot;3x:0,0,0,0,0,0&quot;/>&lt;/Option>&lt;/layer>&lt;/symbol>"/>
          <Option type="double" name="minLength" value="0"/>
          <Option type="QString" name="minLengthMapUnitScale" value="3x:0,0,0,0,0,0"/>
          <Option type="QString" name="minLengthUnit" value="MM"/>
          <Option type="double" name="offsetFromAnchor" value="0"/>
          <Option type="QString" name="offsetFromAnchorMapUnitScale" value="3x:0,0,0,0,0,0"/>
          <Option type="QString" name="offsetFromAnchorUnit" value="MM"/>
          <Option type="double" name="offsetFromLabel" value="0"/>
          <Option type="QString" name="offsetFromLabelMapUnitScale" value="3x:0,0,0,0,0,0"/>
          <Option type="QString" name="offsetFromLabelUnit" value="MM"/>
        </Option>
      </callout>
    </settings>
  </labeling>
  <customproperties>
    <Option type="Map">
      <Option type="List" name="dualview/previewExpressions">
        <Option type="QString" value="&quot;talhao_id&quot;"/>
      </Option>
      <Option type="QString" name="embeddedWidgets/count" value="0"/>
      <Option name="variableNames"/>
      <Option name="variableValues"/>
    </Option>
  </customproperties>
  <blendMode>0</blendMode>
  <featureBlendMode>0</featureBlendMode>
  <layerOpacity>1</layerOpacity>
  <SingleCategoryDiagramRenderer attributeLegend="1" diagramType="Histogram">
    <DiagramCategory scaleBasedVisibility="0" width="15" lineSizeType="MM" spacing="5" spacingUnit="MM" showAxis="1" labelPlacementMethod="XHeight" opacity="1" sizeType="MM" diagramOrientation="Up" height="15" spacingUnitScale="3x:0,0,0,0,0,0" minimumSize="0" penWidth="0" lineSizeScale="3x:0,0,0,0,0,0" direction="0" maxScaleDenominator="1e+08" penColor="#000000" rotationOffset="270" scaleDependency="Area" backgroundAlpha="255" penAlpha="255" backgroundColor="#ffffff" enabled="0" sizeScale="3x:0,0,0,0,0,0" barWidth="5" minScaleDenominator="0">
      <fontProperties style="" description="Ubuntu,11,-1,5,50,0,0,0,0,0"/>
      <attribute field="" color="#000000" label=""/>
      <axisSymbol>
        <symbol type="line" name="" force_rhr="0" alpha="1" clip_to_extent="1">
          <data_defined_properties>
            <Option type="Map">
              <Option type="QString" name="name" value=""/>
              <Option name="properties"/>
              <Option type="QString" name="type" value="collection"/>
            </Option>
          </data_defined_properties>
          <layer enabled="1" class="SimpleLine" locked="0" pass="0">
            <Option type="Map">
              <Option type="QString" name="align_dash_pattern" value="0"/>
              <Option type="QString" name="capstyle" value="square"/>
              <Option type="QString" name="customdash" value="5;2"/>
              <Option type="QString" name="customdash_map_unit_scale" value="3x:0,0,0,0,0,0"/>
              <Option type="QString" name="customdash_unit" value="MM"/>
              <Option type="QString" name="dash_pattern_offset" value="0"/>
              <Option type="QString" name="dash_pattern_offset_map_unit_scale" value="3x:0,0,0,0,0,0"/>
              <Option type="QString" name="dash_pattern_offset_unit" value="MM"/>
              <Option type="QString" name="draw_inside_polygon" value="0"/>
              <Option type="QString" name="joinstyle" value="bevel"/>
              <Option type="QString" name="line_color" value="35,35,35,255"/>
              <Option type="QString" name="line_style" value="solid"/>
              <Option type="QString" name="line_width" value="0.26"/>
              <Option type="QString" name="line_width_unit" value="MM"/>
              <Option type="QString" name="offset" value="0"/>
              <Option type="QString" name="offset_map_unit_scale" value="3x:0,0,0,0,0,0"/>
              <Option type="QString" name="offset_unit" value="MM"/>
              <Option type="QString" name="ring_filter" value="0"/>
              <Option type="QString" name="trim_distance_end" value="0"/>
              <Option type="QString" name="trim_distance_end_map_unit_scale" value="3x:0,0,0,0,0,0"/>
              <Option type="QString" name="trim_distance_end_unit" value="MM"/>
              <Option type="QString" name="trim_distance_start" value="0"/>
              <Option type="QString" name="trim_distance_start_map_unit_scale" value="3x:0,0,0,0,0,0"/>
              <Option type="QString" name="trim_distance_start_unit" value="MM"/>
              <Option type="QString" name="tweak_dash_pattern_on_corners" value="0"/>
              <Option type="QString" name="use_custom_dash" value="0"/>
              <Option type="QString" name="width_map_unit_scale" value="3x:0,0,0,0,0,0"/>
            </Option>
          </layer>
        </symbol>
      </axisSymbol>
    </DiagramCategory>
  </SingleCategoryDiagramRenderer>
  <DiagramLayerSettings priority="0" zIndex="0" linePlacementFlags="18" dist="0" obstacle="0" placement="1" showAll="1">
    <properties>
      <Option type="Map">
        <Option type="QString" name="name" value=""/>
        <Option name="properties"/>
        <Option type="QString" name="type" value="collection"/>
      </Option>
    </properties>
  </DiagramLayerSettings>
  <geometryOptions removeDuplicateNodes="0" geometryPrecision="0">
    <activeChecks/>
    <checkConfiguration type="Map">
      <Option name="QgsGeometryGapCheck" type="Map">
        <Option type="double" name="allowedGapsBuffer" value="0"/>
        <Option type="bool" name="allowedGapsEnabled" value="false"/>
        <Option type="QString" name="allowedGapsLayer" value=""/>
      </Option>
    </checkConfiguration>
  </geometryOptions>
  <legend type="default-vector" showLabelLegend="0"/>
  <referencedLayers/>
  <fieldConfiguration>
    <field configurationFlags="None" name="talhao_id">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="None" name="cod_talhao">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="None" name="fazenda">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="None" name="gleba">
      <editWidget type="Range">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="None" name="propriedad">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="None" name="area_orig_">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="None" name="area_seg_h">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
  </fieldConfiguration>
  <aliases>
    <alias index="0" name="ID do Talhão" field="talhao_id"/>
    <alias index="1" name="Código do Talhão" field="cod_talhao"/>
    <alias index="2" name="Fazenda" field="fazenda"/>
    <alias index="3" name="Gleba" field="gleba"/>
    <alias index="4" name="Propriedade" field="propriedad"/>
    <alias index="5" name="Área Original (ha)" field="area_orig_"/>
    <alias index="6" name="Área Segmentada (ha)" field="area_seg_h"/>
  </aliases>
  <defaults>
    <default applyOnUpdate="0" expression="" field="talhao_id"/>
    <default applyOnUpdate="0" expression="" field="cod_talhao"/>
    <default applyOnUpdate="0" expression="" field="fazenda"/>
    <default applyOnUpdate="0" expression="" field="gleba"/>
    <default applyOnUpdate="0" expression="" field="propriedad"/>
    <default applyOnUpdate="0" expression="" field="area_orig_"/>
    <default applyOnUpdate="0" expression="" field="area_seg_h"/>
  </defaults>
  <constraints>
    <constraint notnull_strength="0" constraints="0" unique_strength="0" exp_strength="0" field="talhao_id"/>
    <constraint notnull_strength="0" constraints="0" unique_strength="0" exp_strength="0" field="cod_talhao"/>
    <constraint notnull_strength="0" constraints="0" unique_strength="0" exp_strength="0" field="fazenda"/>
    <constraint notnull_strength="0" constraints="0" unique_strength="0" exp_strength="0" field="gleba"/>
    <constraint notnull_strength="0" constraints="0" unique_strength="0" exp_strength="0" field="propriedad"/>
    <constraint notnull_strength="0" constraints="0" unique_strength="0" exp_strength="0" field="area_orig_"/>
    <constraint notnull_strength="0" constraints="0" unique_strength="0" exp_strength="0" field="area_seg_h"/>
  </constraints>
  <constraintExpressions>
    <constraint desc="" exp="" field="talhao_id"/>
    <constraint desc="" exp="" field="cod_talhao"/>
    <constraint desc="" exp="" field="fazenda"/>
    <constraint desc="" exp="" field="gleba"/>
    <constraint desc="" exp="" field="propriedad"/>
    <constraint desc="" exp="" field="area_orig_"/>
    <constraint desc="" exp="" field="area_seg_h"/>
  </constraintExpressions>
  <expressionfields/>
  <attributeactions>
    <defaultAction key="Canvas" value="{00000000-0000-0000-0000-000000000000}"/>
  </attributeactions>
  <attributetableconfig sortExpression="" actionWidgetStyle="dropDown" sortOrder="0">
    <columns>
      <column type="field" name="talhao_id" hidden="0" width="-1"/>
      <column type="field" name="cod_talhao" hidden="0" width="-1"/>
      <column type="field" name="fazenda" hidden="0" width="-1"/>
      <column type="field" name="gleba" hidden="0" width="-1"/>
      <column type="field" name="propriedad" hidden="0" width="-1"/>
      <column type="field" name="area_orig_" hidden="0" width="-1"/>
      <column type="field" name="area_seg_h" hidden="0" width="-1"/>
      <column type="actions" hidden="1" width="-1"/>
    </columns>
  </attributetableconfig>
  <conditionalstyles>
    <rowstyles/>
    <fieldstyles/>
  </conditionalstyles>
  <storedexpressions/>
  <editform tolerant="1"></editform>
  <editforminit/>
  <editforminitcodesource>0</editforminitcodesource>
  <editforminitfilepath></editforminitfilepath>
  <editforminitcode><![CDATA[# -*- coding: utf-8 -*-
"""
QGIS forms can have a Python function that is called when the form is
opened.

Use this function to add extra logic to your forms.

Enter the name of the function in the "Python Init function"
field.
An example follows:
"""
from qgis.PyQt.QtWidgets import QWidget

def my_form_open(dialog, layer, feature):
    geom = feature.geometry()
    control = dialog.findChild(QWidget, "MyLineEdit")
]]></editforminitcode>
  <featformsuppress>0</featformsuppress>
  <editorlayout>generatedlayout</editorlayout>
  <editable>
    <field name="area_diff_" editable="1"/>
    <field name="area_dif_1" editable="1"/>
    <field name="area_orig_" editable="1"/>
    <field name="area_seg_h" editable="1"/>
    <field name="background" editable="1"/>
    <field name="backgrou_1" editable="1"/>
    <field name="cod_talhao" editable="1"/>
    <field name="fazenda" editable="1"/>
    <field name="gleba" editable="1"/>
    <field name="gramíne_1" editable="1"/>
    <field name="gramíne_2" editable="1"/>
    <field name="gramíne_3" editable="1"/>
    <field name="gramínea_" editable="1"/>
    <field name="outras_f_1" editable="1"/>
    <field name="outras_fol" editable="1"/>
    <field name="pixel_area" editable="1"/>
    <field name="proc_date" editable="1"/>
    <field name="propriedad" editable="1"/>
    <field name="success" editable="1"/>
    <field name="talhao_id" editable="1"/>
    <field name="total_pixe" editable="1"/>
    <field name="trepadei_1" editable="1"/>
    <field name="trepadeira" editable="1"/>
  </editable>
  <labelOnTop>
    <field name="area_diff_" labelOnTop="0"/>
    <field name="area_dif_1" labelOnTop="0"/>
    <field name="area_orig_" labelOnTop="0"/>
    <field name="area_seg_h" labelOnTop="0"/>
    <field name="background" labelOnTop="0"/>
    <field name="backgrou_1" labelOnTop="0"/>
    <field name="cod_talhao" labelOnTop="0"/>
    <field name="fazenda" labelOnTop="0"/>
    <field name="gleba" labelOnTop="0"/>
    <field name="gramíne_1" labelOnTop="0"/>
    <field name="gramíne_2" labelOnTop="0"/>
    <field name="gramíne_3" labelOnTop="0"/>
    <field name="gramínea_" labelOnTop="0"/>
    <field name="outras_f_1" labelOnTop="0"/>
    <field name="outras_fol" labelOnTop="0"/>
    <field name="pixel_area" labelOnTop="0"/>
    <field name="proc_date" labelOnTop="0"/>
    <field name="propriedad" labelOnTop="0"/>
    <field name="success" labelOnTop="0"/>
    <field name="talhao_id" labelOnTop="0"/>
    <field name="total_pixe" labelOnTop="0"/>
    <field name="trepadei_1" labelOnTop="0"/>
    <field name="trepadeira" labelOnTop="0"/>
  </labelOnTop>
  <reuseLastValue>
    <field name="area_diff_" reuseLastValue="0"/>
    <field name="area_dif_1" reuseLastValue="0"/>
    <field name="area_orig_" reuseLastValue="0"/>
    <field name="area_seg_h" reuseLastValue="0"/>
    <field name="background" reuseLastValue="0"/>
    <field name="backgrou_1" reuseLastValue="0"/>
    <field name="cod_talhao" reuseLastValue="0"/>
    <field name="fazenda" reuseLastValue="0"/>
    <field name="gleba" reuseLastValue="0"/>
    <field name="gramíne_1" reuseLastValue="0"/>
    <field name="gramíne_2" reuseLastValue="0"/>
    <field name="gramíne_3" reuseLastValue="0"/>
    <field name="gramínea_" reuseLastValue="0"/>
    <field name="outras_f_1" reuseLastValue="0"/>
    <field name="outras_fol" reuseLastValue="0"/>
    <field name="pixel_area" reuseLastValue="0"/>
    <field name="proc_date" reuseLastValue="0"/>
    <field name="propriedad" reuseLastValue="0"/>
    <field name="success" reuseLastValue="0"/>
    <field name="talhao_id" reuseLastValue="0"/>
    <field name="total_pixe" reuseLastValue="0"/>
    <field name="trepadei_1" reuseLastValue="0"/>
    <field name="trepadeira" reuseLastValue="0"/>
  </reuseLastValue>
  <dataDefinedFieldProperties/>
  <widgets/>
  <previewExpression>"talhao_id"</previewExpression>
  <mapTip></mapTip>
  <layerGeometryType>2</layerGeometryType>
</qgis>"""
    
    return qml_content

def generate_qgis_styles(results_dir):
    """Gera arquivos de estilo QML simplificados."""
    
    results_path = Path(results_dir)
    
    # Criar arquivo de cores para referência
    colors_info = {
        "classes": {
            0: {"name": "Background", "color": "#787878"},
            1: {"name": "Gramínea Porte Alto", "color": "#ff0000"},
            2: {"name": "Gramínea Porte Baixo", "color": "#00ff00"},
            3: {"name": "Outras Folhas Largas", "color": "#0000ff"},
            4: {"name": "Trepadeira", "color": "#00ffff"}
        }
    }
    
    colors_file = results_path / "cores_classes.json"
    with open(colors_file, 'w', encoding='utf-8') as f:
        json.dump(colors_info, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Referência de cores criada: {colors_file}")
    
    return 1

def create_qgis_instructions(results_dir):
    """Cria arquivo com instruções para usar os resultados no QGIS."""
    
    instructions = """# 🗺️ Instruções para Visualização no QGIS

## 📋 Arquivos Gerados

### 📊 Shapefile Principal
- `resultados_talhoes.shp`: Contém todos os talhões com estatísticas
- Campos importantes: talhao_id, area_orig_, area_seg_h, background, gramínea_, etc.

### 🖼️ GeoTIFFs Individuais  
- `talhao_XX_segmentacao.tif`: Máscaras de segmentação por talhão
- Valores: 0=Background, 1=Gramínea Alto, 2=Gramínea Baixo, 3=Outras Folhas, 4=Trepadeira

### 📄 Relatórios
- `relatorio_consolidado.html`: Relatório visual
- `relatorio_consolidado.json`: Dados estruturados

## 🚀 Passo a Passo no QGIS

1. **Carregar Shapefile**: Camada > Adicionar Camada Vetorial > resultados_talhoes.shp
2. **Explorar Atributos**: Botão direito > Tabela de Atributos
3. **Criar Mapas Temáticos**: Propriedades > Simbologia > Graduado
4. **Adicionar GeoTIFFs**: Camada > Adicionar Camada Raster > talhao_XX_segmentacao.tif

## 🎨 Configuração de Cores para GeoTIFF

1. Propriedades da camada raster > Simbologia
2. Tipo de renderização: Pseudocor de banda única
3. Configurar cores:
   - 0: Cinza (#787878) - Background
   - 1: Vermelho (#ff0000) - Gramínea Porte Alto  
   - 2: Verde (#00ff00) - Gramínea Porte Baixo
   - 3: Azul (#0000ff) - Outras Folhas Largas
   - 4: Ciano (#00ffff) - Trepadeira

Boa análise! 🌾
"""
    
    instructions_file = Path(results_dir) / "INSTRUCOES_QGIS.md"
    with open(instructions_file, 'w', encoding='utf-8') as f:
        f.write(instructions)
    
    print(f"📋 Instruções QGIS criadas: {instructions_file}")
    return instructions_file

def main():
    """Gera estilos e instruções para resultados existentes."""
    
    # Verificar se há resultados para processar
    current_dir = Path(".")
    results_dirs = [d for d in current_dir.iterdir() if d.is_dir() and 'resultado' in d.name.lower()]
    
    if not results_dirs:
        print("❌ Nenhum diretório de resultados encontrado")
        print("Execute primeiro o processamento:")
        print("python ortofoto_inference_talhoes.py --area-dir '...' --use-plots")
        return
    
    for results_dir in results_dirs:
        print(f"\n🎨 Processando: {results_dir}")
        
        # Verificar se há shapefile
        shapefile = results_dir / "resultados_talhoes.shp"
        if not shapefile.exists():
            print(f"⚠️  Shapefile não encontrado em {results_dir}")
            continue
        
        # Gerar estilos
        num_styles = generate_qgis_styles(results_dir)
        print(f"📊 {num_styles} estilos QML criados")
        
        # Gerar instruções
        create_qgis_instructions(results_dir)
        
        print(f"✅ {results_dir} preparado para QGIS!")

if __name__ == "__main__":
    main()
