## Instructions for installation

```bash
cmsrel CMSSW_8_1_0
cd CMSSW_8_1_0/src/
cmsenv

git clone https://github.com/cms-analysis/HiggsAnalysis-CombinedLimit.git HiggsAnalysis/CombinedLimit
cd HiggsAnalysis/CombinedLimit
git checkout v7.0.12
cd $CMSSW_BASE/src

git clone -b HIG-19-008-backup https://github.com/HEP-KBFI/CombineHarvester.git CombineHarvester

scram b -j 8
```
