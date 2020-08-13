library(lme4)
library(ggplot2)
library("plyr")

df <- read.table("data/IPCC_2019_Weight_gain.csv", 
                 header = TRUE,
                 sep = ";",
                 encoding = "UTF-8")
mod <- lm(log(WG) ~ Intake, data=df)
#mod <- lm(Milk_yield ~ Concentrate_intake + Grass_intake, data=df_temperate)
summary(mod)
par(mfrow = c(2, 2))
plot(mod)
df$predlm <- predict(mod)

ggplot(df,aes(x=Intake, y=WG)) +
  geom_point(size=3) + 
  geom_line(aes(y = exp(predlm)), size = 1.5)+
  labs(y="Weight gain (kg/head/day)", x = "Concentrate intake (kgDM/year)")+
  theme(axis.title = element_text(size = 18),
        legend.text = element_text(size = 18),
        legend.title = element_text(face = "bold",size = 18))

coef_final<-data.frame(t(mod$coefficients))
colnames(coef_final)<- c("Intercept","Intake")
# coef_final[is.na(coef_final)] <- 0
write.csv(coef_final,'output/coefficients_weight_gain_intake_no_dairy_relation.csv')

mod <- lm(EF ~ Intake, data=df)
#mod <- lm(Milk_yield ~ Concentrate_intake + Grass_intake, data=df_temperate)
summary(mod)
par(mfrow = c(2, 2))
plot(mod)
df$predlm <- predict(mod)

ggplot(df,aes(x=Intake, y=EF)) +
  geom_point(size=3) + 
  geom_line(aes(y = predlm), size = 1.5)+
  labs(y="EF (kgCH4/head/year)", x = "Concentrate intake (kgDM/year)")+
  theme(axis.title = element_text(size = 18),
        legend.text = element_text(size = 18),
        legend.title = element_text(face = "bold",size = 18))

coef_final<-data.frame(t(mod$coefficients))
colnames(coef_final)<- c("Intercept","Intake")
# coef_final[is.na(coef_final)] <- 0
write.csv(coef_final,'output/coefficients_EF_intake_no_dairy_relation.csv')
