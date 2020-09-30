library(lme4)
library(ggplot2)
library("plyr")

#Read data
df <- read.table("output/meat_intake_non_dairy.csv", 
                 header = TRUE,
                 sep = ";",
                 quote="\"",
                 encoding = "UTF-8")

df["Production_rate"]=df["Production"]/df["Number"]
df["Total_intake_rate"]=df["Total_intake"]/df["Number"]

#Fit model
mod <- lm(Production_rate ~ Total_intake_rate + factor(GAEZ), data=df)
summary(mod)
par(mfrow = c(2, 2))
plot(mod)
df$predlm <- predict(mod)

#Plot model and data
ggplot(df,aes(x=Total_intake_rate, y=Production_rate,color=factor(GAEZ))) +
  geom_point(size=3) + 
  geom_line(aes(y = predlm), size = 1.5)+
  labs(y="Carcass weight (kg/head/year)", x = "Total intake (kgDM/year)")+
  theme(axis.title = element_text(size = 18),
        legend.text = element_text(size = 18),
        legend.title = element_text(face = "bold",size = 18))

#Save coefficients
coef_final<-data.frame(t(mod$coefficients))
colnames(coef_final)<- c("Intercept","Intake","GAEZ")
# coef_final[is.na(coef_final)] <- 0
write.csv(coef_final,'output/coefficients_weight_intake_no_dairy_relation.csv')
