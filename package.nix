{ lib
, pkgs
, my_python
, neontology
}:
with pkgs;

python3.pkgs.buildPythonPackage rec {
  pname = "mindwm-knfunc";
  version = "0.1.0";

  src = ./.;

  propagatedBuildInputs = [ dependencies ];
  dependencies = with my_python.pkgs; [
    pandas
    pydantic dateutil urllib3
    opentelemetry-sdk opentelemetry-exporter-otlp
    neo4j
    fastapi uvicorn
    neontology
    pyyaml
    openai
  ];

  pythonImportsCheck = [
    "mindwm.model"
    "mindwm.model.events"
    "mindwm.model.graph"
    "neontology"
  ];
  format = "pyproject";
  nativeBuildInputs = with python3.pkgs; [ setuptools ];
}
