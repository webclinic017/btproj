rm report/*
rm plot/*
az webapp up --sku F1 --name feitrade2 --runtime "PYTHON|3.8" -g trade2 -p ASP-trade2-8532 -l eastasia