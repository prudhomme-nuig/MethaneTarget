library(lme4)
library(ggplot2)
library("plyr")
library(viridis)

#Read emissions data
df <- read.table("output/pigs_meat_emission_intake.csv", 
                 header = TRUE,
                 sep = ",",
                 quote="\"",
                 encoding = "UTF-8")

df["Meat_rate"]=df["Meat"]/df["Number"]
df["Grain_intake_rate"]=df["Grain_intake"]/df["Number"]

#Fit model
mod <- lm(Meat_rate ~ Grain_intake_rate, data=df)
summary(mod)
par(mfrow = c(2, 2))
plot(mod)
df$predlm <- predict(mod)

#Plot model and data
ggplot(df,aes(x=Grain_intake_rate, y=Meat_rate)) +
  geom_point(size=3) + 
  geom_line(aes(y = predlm), size = 1.5)+
  labs(y="Carcass weight (tCW/year)", x = "Grain intake (tDM/year)")+
  theme(axis.title = element_text(size = 18),
        legend.text = element_text(size = 18),
        legend.title = element_text(face = "bold",size = 18))

#Save coefficients
coef_final<-data.frame(t(mod$coefficients))
colnames(coef_final)<- c("Intercept","Grain_intake")
# coef_final[is.na(coef_final)] <- 0
write.csv(coef_final,'output/coefficients_weight_intake_pigs_relation.csv')
