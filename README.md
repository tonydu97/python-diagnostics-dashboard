# python-diagnostics-dashboard
M&A Diagnostics dashboard using Dash and Plotly 


# REQUIRED PYTHON PACKAGES
Pandas (comes with Anaconda)
Numpy (comes with Anaconda)
Dash ("conda install -c conda-forge dash" in Anaconda powershell)
Dash Bootstrap Components ("conda install -c conda-forge dash-bootstrap-components" in Anaconda powershell)

# INSTRUCTIONS



modify and run 'rundiagnostics.py' code to generate input file
open Anaconda Powershell
navigate to code folder directory
run 'python app.py'
visit local url generated (should be http://127.0.0.1:8050/)


# CHANGELOG


v1.1 Beta 5/4/20

Updates
- Fix Top Players Pie Chart
- Changed Phase3x4x graph into datatable

To-Do
- Add MCP and Wheeling rate Information to dashboard (already generated in input file)
- Card/Tab resizing 
- Add MCP and AEC vs Non-Eco distinction to Supply Curve



v1 Beta 4/26/20

Updates
- initial version
- Supported Diagnostics:
    - MMfile Summary (Generation, Load, Transmission)
    - Top Players
    - Phase3x4x by DM by Period
    - Supply Curve and MCP Sensitivity (partial WIP)



To-Do
- Add MCP and Wheeling rate Information to dashboard (already generated in input file)
- Fix Top Players Pie Chart to show combined non Top Players
- Add MCP and AEC vs Non-Eco distinction to Supply Curve
- Fix card resizing

