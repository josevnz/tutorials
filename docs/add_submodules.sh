#!/bin/bash
:<<DOC
Note to self: Run every time a new tutorial on an external repository is added :-D
DOC
declare -a submodules
submodules=(
"EmpireStateBuildingRunUp"
"home_nmap"
"kismet_home"
"BashError"
"InteractiveBashScript"
"DatesAndComplexInBash"
"BashResources"
"rpm_query"
"EnableSysadminRssReader"
"ExtendingAnsibleWithPython"
"grafana"
"insecure_protocol_tutorial"
"influxdb_intro"
"influxdb_datasets"
"GlancesAndInfluxDB.git"
"OracleCloudHomeLab"
"SuricataLog"
"yafd"
"nyrr"
"Nexus3OnOrangePI"
"StopUsingTelnetToTestPorts"
"BashHere"
"DebuggingApplications"
"Covid19Informer"
"Falco"
"linktester"
"CommandLineTipsAndTricks"
)

for module in ${submodules[*]}; do
	if [[ ! -d $module ]]; then
	    if ! git submodule add "https://github.com/josevnz/${module}"; then
                echo "ERROR: Could not add submodule $modulei -> git submodule add 'https://github.com/josevnz/${module}'"
                exit 100
            fi
  fi
  echo "[$module]($module/README.md)"
done
