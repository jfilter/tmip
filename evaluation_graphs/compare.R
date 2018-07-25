library(ggplot2)

df<- read.table(text = "Dataset Accuracy Model
1 0.10vs0.10  0.703432 Baseline
2 0.10vs0.10 0.7195692883 Best
3 0.25vs0.25 0.641323 Baseline
4 0.25vs0.25 0.6893258427 Best
5 0.50vs0.50 0.604321 Baseline
6 0.50vs0.50 0.625 Best", header = TRUE, sep = "")


p<-ggplot(data=df, aes(Dataset, Accuracy, fill=Model)) +
  geom_bar(position = "dodge", stat="identity") + 
  scale_fill_manual(values=c("#919191","#032e7a")) +
  geom_text(aes(label=round(Accuracy, digits = 4)), position=position_dodge(width=0.9), vjust=-0.25) +
  theme_bw() + 
  coord_cartesian(ylim = c(0.5, 0.75)) +
  theme(panel.grid.major.x = element_blank(), panel.grid.minor = element_blank(), axis.title.x=element_blank())

p

ggsave(filename="exp_comp.png", plot=p, width=6, height=3)