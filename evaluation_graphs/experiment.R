library(ggplot2)

# df <- data.frame(
#   Model = factor(c("Baseline",	"CNN",	"LSTM", "GRU"	,"Stacked LSTM"	,"Stacked GRU"), levels=c("Baseline",	"CNN",	"LSTM", "GRU"	,"Stacked LSTM"	,"Stacked GRU")),
#   Accuracy = c(0.604321, 0.6140449439, 0.6234082397, 0.625, 0.6176966292, 0.6190074907)
# )

# df <- data.frame(
#   Model = factor(c("Baseline",	"CNN",	"LSTM", "GRU"	,"Stacked LSTM"	,"Stacked GRU"), levels=c("Baseline",	"CNN",	"LSTM", "GRU"	,"Stacked LSTM"	,"Stacked GRU")),
#   Accuracy = c(0.703432, 0.7195692883, 0.7144194757, 0.7130149813, 0.7083333331, 0.711610487)
# )

df <- data.frame(
  Model = factor(c("Baseline",	"CNN",	"LSTM", "GRU"	,"Stacked LSTM"	,"Stacked GRU"), levels=c("Baseline",	"CNN",	"LSTM", "GRU"	,"Stacked LSTM"	,"Stacked GRU")),
  Accuracy = c(0.641323, 0.6780898877, 0.6820224718, 0.6887640448, 0.6846441948, 0.6893258427)
)


df$fill <- ifelse(df$Model == "Baseline", "#a6cee3", ifelse(df$Accuracy == max(df$Accuracy, na.rm = TRUE), "#b2df8a", "#1f78b4"))

p<-ggplot(data=df, aes(x=Model, y=Accuracy, fill=fill)) +
  geom_bar(stat="identity") +
  geom_text(aes(label=round(Accuracy, digits = 4)), position=position_dodge(width=0.9), vjust=-0.25) +
  scale_fill_manual("legend", values = c("Baseline" = "black", "CNN" = "orange", "LSTM" = "blue")) + 
  coord_cartesian(ylim = c(0.5, 0.75)) +
  scale_fill_identity() + 
  theme_bw() + 
  theme(panel.grid.major.x = element_blank(), panel.grid.minor = element_blank(), axis.title.x=element_blank())
p
ggsave(filename="exp_2.png", plot=p, width=6, height=3)
