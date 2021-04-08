library(lme4)
library(ggplot2)
library("plyr")
library(viridis)

#Read emissions data
df <- read.table("output/poultry_meat_eggs_emission_intake.csv", 
                 header = TRUE,
                 sep = ",",
                 quote="\"",
                 encoding = "UTF-8")

############ Meat ####################

df["Meat_rate"]=df["Meat"]/df["Number_poultry"]
df["Grain_intake_poultry_rate"]=df["Grain_intake_poultry"]/df["Number_poultry"]

df<-df[df$Grain_intake_poultry_rate<0.06,]

#Fit model
mod <- lm(Meat_rate ~ Grain_intake_poultry_rate, data=df)
summary(mod)
par(mfrow = c(2, 2))
plot(mod)
df$predlm <- predict(mod)

#Plot model and data
ggplot(df,aes(x=Grain_intake_poultry_rate*1E3, y=Meat_rate*1E3)) +
  geom_point(size=3) + 
  geom_line(aes(y = predlm*1E3), size = 1.5)+
  labs(y="Carcass weight (kgCW/year)", x = "Grain intake (kgDM/year)")+
  theme(axis.title = element_text(size = 18),
        legend.text = element_text(size = 18),
        legend.title = element_text(face = "bold",size = 18))

#Save coefficients
coef_final<-data.frame(t(mod$coefficients))
colnames(coef_final)<- c("Intercept","Grain_intake")
# coef_final[is.na(coef_final)] <- 0
write.csv(coef_final,'output/coefficients_weight_intake_poultry_relation.csv')

############ Eggs ####################

df["Eggs_rate"]=df["Eggs"]/df["Number_layer"]
df["Grain_intake_layers_rate"]=df["Grain_intake_layers"]/df["Number_layer"]

#Fit model
mod <- lm(Eggs_rate ~ Grain_intake_layers_rate, data=df)
summary(mod)
par(mfrow = c(2, 2))
plot(mod)
df$predlm <- predict(mod)

#Plot model and data
ggplot(df,aes(x=Grain_intake_layers_rate, y=Eggs_rate)) +
  geom_point(size=3) + 
  geom_line(aes(y = predlm), size = 1.5)+
  labs(y="Eggs (t/year)", x = "Grain intake (tDM/year)")+
  theme(axis.title = element_text(size = 18),
        legend.text = element_text(size = 18),
        legend.title = element_text(face = "bold",size = 18))

#Save coefficients
coef_final<-data.frame(t(mod$coefficients))
colnames(coef_final)<- c("Intercept","Grain_intake")
# coef_final[is.na(coef_final)] <- 0
write.csv(coef_final,'output/coefficients_eggs_intake_poultry_relation.csv')

