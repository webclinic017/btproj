rm report/*
rm plot/*
az webapp up --sku F1 --name feitrade --runtime "PYTHON|3.8" -g emmelle_0_rg_Linux_southcentralus -p emmelle_0_asp_Linux_southcentralus_0 -l southcentralus