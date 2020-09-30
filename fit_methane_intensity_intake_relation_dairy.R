library(lme4)

df <- read.table("output/data_dairy_for_lm.csv", 
                 header = TRUE,
                 sep = ",",
                 encoding = "UTF-8")

df_temperate<-df#[df["GAEZ"]=="Temperate",]
df_temperate["Methane"]<-df_temperate["Methane_intensity"]/df_temperate["Milk_yield"]
mod_temparate <- lm(Methane_intensity ~ poly(Concentrate_intake,2) + factor(GAEZ), data=df_temperate)
#mod <- lm(Milk_yield ~ Concentrate_intake + Grass_intake, data=df_temperate)
summary(mod_temparate)
par(mfrow = c(2, 2))
plot(mod_temparate)
df_temperate$predlm <- predict(mod_temparate)

ggplot(df_temperate,aes(x=Concentrate_intake, y=Methane_intensity,color=factor(GAEZ))) +
  geom_point(size=3) + 
  geom_line(aes(y = predlm), size = 1.5)+
  scale_color_discrete(name = "GAEZ:", labels = c("Temperate cool", "Tropical warm"))+
  labs(y="Methane intensity (kgCH4/kg milk/year)", x = "Concentrate intake (tDM/year)")+
  theme(axis.title = element_text(size = 18),
        legend.text = element_text(size = 18),
        legend.title = element_text(face = "bold",size = 18))

  library("plyr")
coef_final<-as.data.frame.list(mod_temparate$coefficients)
colnames(coef_final)<- c("Intercept","Concentrate_intake","Concentrate_intake_2","GAEZ")
write.csv(coef_final,'output/coefficients_methane_intensity_concentrate_relation.csv')