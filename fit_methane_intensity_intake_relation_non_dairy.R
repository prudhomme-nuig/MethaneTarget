library(lme4)
library(ggplot2)
library("plyr")

#Read data
df <- read.table("output/meat_intake_non_dairy.csv", 
                 header = TRUE,
                 sep = ";",
                 quote="\"",
                 encoding = "UTF-8")
df["Methane_intensity"]=df["Methane"]/df["Number"]
df["Concentrate_intake_rate"]=df["Concentrate_intake"]/df["Number"]
df["Total_intake_rate"]=df["Total_intake"]/df["Number"]

#Fit model
mod <- lm(Methane_intensity ~ Total_intake_rate, data=df)
summary(mod)
par(mfrow = c(2, 2))
plot(mod)

#Plot model and data
df$predlm <- predict(mod)
ggplot(df,aes(x=Total_intake_rate, y=Methane_intensity,colour=GAEZ)) +
  geom_point(size=3) + 
  geom_line(aes(y = predlm), size = 1.5)+
  labs(y="Methane intensity (kgCH4/head/yr)", x = "Intake (kgDM/year)")+
  theme(axis.title = element_text(size = 18),
        legend.text = element_text(size = 18),
        legend.title = element_text(face = "bold",size = 18))

#Save coefficients
coef_final<-data.frame(t(mod$coefficients))
colnames(coef_final)<- c("Intercept","Intake")
# coef_final[is.na(coef_final)] <- 0
write.csv(coef_final,'output/coefficients_weight_intake_no_dairy_relation.csv')
