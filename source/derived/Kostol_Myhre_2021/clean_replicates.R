library(readxl)

Main <- function(){
  paper  <- "Kostol_Myhre_2021"
  indir  <- "datastore/raw/bootstrap_census/Kostol_Myhre_2021/orig"
  outdir <- "output/derived/bootstrap_census"
  
  precision_file <- "source/derived/bootstrap_census/digits_after_comma_precision.txt"
  n_digits <- as.numeric(read.table(precision_file, quote="\"", comment.char=""))
  
  PrepareReplicatesAndEstimates(paper, indir, outdir, n_digits)
}

PrepareReplicatesAndEstimates <- function(paper, indir, outdir, n_digits){
  table3 <- read_excel(sprintf("%s/bootstrap_tab3&4.xlsx", indir), sheet = "tab3", col_names = FALSE, skip = 6)
  table4 <- read_excel(sprintf("%s/bootstrap_tab3&4.xlsx", indir), sheet = "tab4", col_names = FALSE, skip = 5)
  
  FractionNonoptimizers <- unlist(as.vector(table3[,2]))
  ObservedBunchingElasticity <- unlist(as.vector(table3[,4]))
  StructuralElasticity <- unlist(as.vector(table3[,5]))
  
  EarningsElasticityInformed <- unlist(as.vector(table4[,5]))
  EarningsElasticityNoninformed <- unlist(as.vector(table4[,10]))
  
  output<-rbind(rep("FractionNonoptimizers",length(FractionNonoptimizers)),1:length(FractionNonoptimizers),FractionNonoptimizers)
  
  df <- as.data.frame(c(rep("FractionNonoptimizers",length(FractionNonoptimizers)),
                        rep("ObservedBunchingElasticity",length(ObservedBunchingElasticity)),
                        rep("StructuralElasticity",length(StructuralElasticity)),
                        rep("EarningsElasticityInformed",length(EarningsElasticityInformed)),
                        rep("EarningsElasticityNoninformed",length(EarningsElasticityNoninformed))))
  df <- cbind(df,rep(1:500,5))
  df <- cbind(df, round(c(FractionNonoptimizers, ObservedBunchingElasticity, 
                          StructuralElasticity, EarningsElasticityInformed, 
                          EarningsElasticityNoninformed),digits=n_digits))
  colnames(df) <- c("object","replicate_number","replicate_value")
  
  df2 <- as.data.frame(c("FractionNonoptimizers","ObservedBunchingElasticity",
                         "StructuralElasticity","EarningsElasticityInformed",
                         "EarningsElasticityNoninformed"))
  df2 <- cbind(df2, c(0.387,0.087,0.286,0.150,0.058))
  df2 <- cbind(df2, round(c(sd(FractionNonoptimizers), sd(ObservedBunchingElasticity), 
                            sd(StructuralElasticity), sd(EarningsElasticityInformed), 
                            sd(EarningsElasticityNoninformed)),digits=n_digits))
  colnames(df2) <- c("object","estimate","std_err")
  
  write.csv(df,sprintf('%s/%s_Replicates.csv', outdir, paper),row.names=FALSE)
  write.csv(df2,sprintf('%s/%s_Estimates.csv', outdir, paper),row.names=FALSE)
}

Main()
