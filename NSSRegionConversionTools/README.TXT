-------------------------------------------------
1/4/2016
Martyn Smith
Region Grid Tools

Environment: ArcGIS 10.3.1
Purpose:  To flatten a set of input region grids to a single polygon shapefile that will be used to overlay with a streamstats basin
Contains:  mergeRegionGrids.tbx and submodel.tbx
-------------------------------------------------

 Instructions:

1) for a specific state or region, go into "bc_layers" folder and create a new Folder called "regionService"

2) Get list of region grids from state XML "ApLayer Name" ie:

	<ApLayers TagName="RegionLayers">
          <ApLayer Name="pkregion_gr2" TagName="PeakFlows" AliasName="pkregion_gr2" Desc="Peak Flows Region Grid" FeatureType="1" ShapeType="1" CanCreate="0" LayerType="1" TargetLocation="" TargetDatasets="" AdditionalParams="ISWATERSHEDAREA=1;FLOWSDISPLAYORDER=PK1_25,PK1_5,PK2,PK5,PK10,PK25,PK50,PK100,PK200,PK500">
            <ApLayers TagName="ApLayers">
              <ApLayer Name="HUCPeakFlowRegions" TagName="HUCRegionsTable" AliasName="HUCPeakFlowRegions" Desc="HUCRegionsTable" FeatureType="0" ShapeType="7" CanCreate="8" LayerType="10" TargetLocation="" TargetDatasets="">
              </ApLayer>
            </ApLayers>
          </ApLayer>
          <ApLayer Name="bkfullreg_g" TagName="BankFullFlows" AliasName="bkfullreg_g" Desc="Bank Full Region Grid" FeatureType="1" ShapeType="1" CanCreate="0" LayerType="1" TargetLocation="" TargetDatasets="" AdditionalParams="ISWATERSHEDAREA=1">
            <ApLayers TagName="ApLayers">
              <ApLayer Name="HUCBankFullRegions" TagName="HUCRegionsTable" AliasName="HUCBankFullRegions" Desc="HUCRegionsTable" FeatureType="0" ShapeType="7" CanCreate="8" LayerType="10" TargetLocation="" TargetDatasets="">
              </ApLayer>
            </ApLayers>
          </ApLayer>
        </ApLayers>

3) Copy these grids out to a new folder ie: "D:\ss_data\ny\bc_layers\regionService"

3) Open the tool "mergeRegionGrids" and set the "Input Path" to "D:\ss_data\ny\bc_layers\regionService"

4) Set the "Region Table" to "regionequationID-citationID.csv"

5) Set the state abbreviation field

6) Name the output shapefile

7)when script is finished copy the shapefile from "D:\ss_data\ny\bc_layers\regionService" to the file GDB

