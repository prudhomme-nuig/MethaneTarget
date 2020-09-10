library(lme4)
library(ggplot2)
library("plyr")

#Read data
df <- read.table("data/IPCC_2019_Weight_gain.csv", 
                 header = TRUE,
                 sep = ";",
                 encoding = "UTF-8")

ggplot(df,aes(x=WG, y=EF)) +
  geom_point(size=3) + 
  #geom_line(aes(y = predlm), size = 1.5)+
  #labs(y="EF (kgCH4/head/year)", x = "Intake (kgDM/year)")+
  theme(axis.title = element_text(size = 18),
        legend.text = element_text(size = 18),
        legend.title = element_text(face = "bold",size = 18))

#Relation between weight gain (WG) and feed intake
mod <- lm(log(WG) ~ Intake, data=df)
summary(mod)
par(mfrow = c(2, 2))
plot(mod)
df$predlm <- predict(mod)

ggplot(df,aes(x=Intake, y=WG)) +
  geom_point(size=3) + 
  geom_line(aes(y = exp(predlm)), size = 1.5)+
  labs(y="Weight gain (kg/head/day)", x = "Intake (kgDM/year)")+
  theme(axis.title = element_text(size = 18),
        legend.text = element_text(size = 18),
        legend.title = element_text(face = "bold",size = 18))

coef_final<-data.frame(t(mod$coefficients))
colnames(coef_final)<- c("Intercept","Intake")
# coef_final[is.na(coef_final)] <- 0
write.csv(coef_final,'output/coefficients_weight_gain_intake_no_dairy_relation.csv')

#Relation between emission intensity (EF) and feed intake
mod <- lm(EF ~ Intake, data=df)
summary(mod)
par(mfrow = c(2, 2))
plot(mod)
df$predlm <- predict(mod)

ggplot(df,aes(x=Intake, y=EF)) +
  geom_point(size=3) + 
  geom_line(aes(y = predlm), size = 1.5)+
  labs(y="EF (kgCH4/head/year)", x = "Intake (kgDM/year)")+
  theme(axis.title = element_text(size = 18),
        legend.text = element_text(size = 18),
        legend.title = element_text(face = "bold",size = 18))

coef_final<-data.frame(t(mod$coefficients))
colnames(coef_final)<- c("Intercept","Intake")
# coef_final[is.na(coef_final)] <- 0
write.csv(coef_final,'output/coefficients_EF_intake_no_dairy_relation.csv')

mod <- lm(log(Weight) ~ Intake + factor(Herd), data=df)
summary(mod)
par(mfrow = c(2, 2))
plot(mod)
df$predlm <- predict(mod)
ggplot(df,aes(x=Intake, y=Weight,colour=Herd)) +
  geom_point(size=3) + 
  geom_line(aes(y = exp(predlm)), size = 1.5)+
  labs(y="Weight", x = "Intake (kgDM/year)")+
  theme(axis.title = element_text(size = 18),
        legend.text = element_text(size = 18),
        legend.title = element_text(face = "bold",size = 18))

coef_final<-data.frame(t(mod$coefficients))
colnames(coef_final)<- c("Intercept","Intake")
# coef_final[is.na(coef_final)] <- 0
write.csv(coef_final,'output/coefficients_weight_intake_no_dairy_relation.csv')

df <- read.table("output/data_non-dairy_for_lm.csv", 
                 header = TRUE,
                 sep = ",",
                 encoding = "UTF-8")

mod <- lm(log(Weight) ~ Intake + factor(Herd), data=df)
summary(mod)
par(mfrow = c(2, 2))
plot(mod)
df$predlm <- predict(mod)
ggplot(df,aes(x=Intake, y=Weight,colour=Herd)) +
  geom_point(size=3) + 
  geom_line(aes(y = exp(predlm)), size = 1.5)+
  labs(y="Weight", x = "Intake (kgDM/year)")+
  theme(axis.title = element_text(size = 18),
        legend.text = element_text(size = 18),
        legend.title = element_text(face = "bold",size = 18))

coef_final<-data.frame(t(mod$coefficients))
colnames(coef_final)<- c("Intercept","Intake","Calves on milk","Feedlot cattle","Growing heifers/steers","Growing/Replacement","Replacement/growing")
# coef_final[is.na(coef_final)] <- 0
write.csv(coef_final,'output/coefficients_weight_intake_no_dairy_relation.csv')

df <- read.table("output/data_non-dairy_for_lm.csv", 
                 header = TRUE,
                 sep = ",",
                 encoding = "UTF-8")

mod <- lm(Methane_intensity ~ Total_intake, data=df)
summary(mod)
par(mfrow = c(2, 2))
plot(mod)
df$predlm <- predict(mod)
ggplot(df,aes(x=Total_intake, y=Methane_intensity,colour=GAEZ)) +
  geom_point(size=3) + 
  #geom_line(aes(y = exp(predlm)), size = 1.5)+
  labs(y="Meat yield", x = "Intake (kgDM/year)")+
  theme(axis.title = element_text(size = 18),
        legend.text = element_text(size = 18),
        legend.title = element_text(face = "bold",size = 18))
