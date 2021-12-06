# 6242project
Crime Analysis and Visualization in Atlanta Based on Spatio-Temporal Kernel Density Estimation (STKDE)

Team 12: Jingjing Ye, Guangyu Min, Ziheng Xiao

## DESCRIPTION
The project code contains two parts: 
1. Data analysis: including refined data, STKDE output data, prediction data, STKDE code
2. Data Visualization: including front-end visualization result, and user interface

## INSTALLATION


To view the visualization result, visit
https://kratosst.github.io. For the data presented in the demo, visit the corresponding github page (https://github.com/KratosST/kratosst.github.io) for presented data.

## EXECUTION
There are several files to process the data. These codes are designed for data merging, refining and scaling. 

Crime Map Visualization Interaction:

1.The bottom slider defines the time range from Jan 1, 2009 to Nov 1, 2021. Draw the slider to select a single day and view the heatmap.

2.The dropdown bar defines the splitted hour range in a single day. Select one period and view its the heatmap data for a specific day chosen in step 1. 

3.Move mouse on each neighborhood to view the previous crime analysis. 

4.Click on the map to see the crime analysis with prediction on a specific region grid. The grid size is predefined and used in STKDE and prediction. 
