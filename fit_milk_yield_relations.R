library(lme4)

df <- read.table("output/data_for_lm.csv", 
                 header = TRUE,
                 sep = ",",
                 encoding = "UTF-8")

df_temperate<-df#[df["GAEZ"]=="Temperate",]
mod_temparate <- lm(log(Milk_yield) ~ poly(Concentrate_intake,2) + factor (GAEZ), data=df_temperate)
#mod <- lm(Milk_yield ~ Concentrate_intake + Grass_intake, data=df_temperate)
summary(mod_temparate)
par(mfrow = c(2, 2))
plot(mod_temparate)
df_temperate$predlm <- predict(mod_temparate)

ggplot(df_temperate,aes(x=Concentrate_intake, y=Milk_yield,color=factor(GAEZ),shape=factor(GAEZ))) +
  geom_point(size=3) + 
  geom_line(aes(y = exp(predlm)), size = 1.5)+
  #scale_color_discrete(name = "Grass intake:", labels = c("2 tDM/year", "3 tDM/year", "4 tDM/year"))+
  labs(y="Milk yield (t/year)", x = "Concentrate intake (tDM/year)")+
  theme(axis.title = element_text(size = 18),
        legend.text = element_text(size = 18),
        legend.title = element_text(face = "bold",size = 18))

df_tropical<-df[df["GAEZ"]=="Tropical",]
mod_tropical <- lm(Milk_yield ~ poly(Concentrate_intake,2)  , data=df_tropical)
#mod <- lm(Milk_yield ~ Concentrate_intake + Grass_intake, data=df_tropical)
summary(mod_tropical)
par(mfrow = c(2, 2))
plot(mod_tropical)
df_tropical$predlm <- predict(mod_tropical)


ggplot(df_tropical,aes(x=Concentrate_intake, y=Milk_yield,color=factor(Grass_intake_cat))) +
  geom_point(size=3) + 
  geom_line(aes(y = predlm), size = 1.5)+
  scale_color_discrete(name = "Grass intake:", labels = c("1 tDM/year", "2 tDM/year", "3 tDM/year"))+
  labs(y="Milk yield (t/year)", x = "Concentrate intake (tDM/year)")+
  theme(axis.title = element_text(size = 18),
        legend.text = element_text(size = 18),
        legend.title = element_text(face = "bold",size = 18))

library("plyr")
coef_final<-rbind.fill(as.data.frame.list(mod_temparate$coefficients),as.data.frame.list(mod_tropical$coefficients))
colnames(coef_final)<- c("Intercept","Concentrate_intake","Concentrate_intake_2","Grass_intake_cat.3","factor.Grass_intake_cat.4")
rownames(coef_final)<-c("Temparate","Tropical")
coef_final[is.na(coef_final)] <- 0
write.csv(coef_final,'output/coefficients_milk_yield_concentrate_relation.csv')
