# install the R package
require("foreign")

# note must have hash and VGAM package installed to run pph
require("hash")
require("VGAM")
install.packages('pph', repos='http://laats.github.io/sw/R')
require('pph')

# get command line arguments
options(echo=TRUE)
args <- commandArgs(trailingOnly = TRUE)

data <- read.csv(args[1])

# scale into data into unit interval
data <- to01(data)

summary(data)

e <- as.numeric(args[2])

print(log(nrow(data)))

newdata <- pdata(data, eps=e)
summary(newdata)
write.arff(newdata, file = "newdata.arff")
