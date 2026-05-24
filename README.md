# OT IDS Thesis Test Environment

This repository contains the implementation and experimental artifacts developed for the bachelor thesis:

**Anomaly Detection in Operational Technology Environments: Assessing the Detection Capabilities of Individual Network and Process Features.**

The project revolves around anomaly detection on individual behavorial indicators in Operational Technology (OT) through the use of:
- A simulated OT environment using OpenPLC Editor and OpenPLC Runtime.
- A rule-based anomaly IDS tailored to the environment.
- Two unsupervised machine learning models (Isolation Forest and One-Class SVM)
- Process- and network-level data gathering
- Feature-specific attack generation

## Directory Contents
- `/openplc`
  - PLC simulation and OpenPLC project files
 
- `/anomaly-detector`
   - Isolation Forest and One-Class SVM implementation
   - Rule-based IDS implementation

- `/anomaly-detector/captures`
  - Network capture scripts and generated traffic

- `/attacks`
  - Scripts for generating modified datasets and attack scenarios

- `/logs`
  - Generated datasets and merged logs
 
## Setup:
Clone the repository:
git clone https://github.com/LudAllinger/ot-feature-reliability-analysis.git

Download and Install OpenPLC IDE and Runtime:
- https://autonomylogic.com/download
- https://github.com/thiagoralves/OpenPLC_v3

## Notes
This repository is reseach-oriented and specifically tailored to the OT testbed used in the thesis.
It is not intended as a production-ready IDS solution.

## Authors
* Ludvig Allinger
* Amelie Bobadilla

## License
This project is licensed under the MIT License
