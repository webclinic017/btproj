rm report/*
rm plot/*
az webapp up --sku F1 --name feitrade3 --runtime "PYTHON|3.10" -g trade3 -p ASP-trade3-8d4b -l japanwest