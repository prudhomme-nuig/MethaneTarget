library(lme4)
library(ggplot2)
library("plyr")

#Read activity data
df <- read.table("data/FAOSTAT_animal_yields.csv", 
                 header = TRUE,
                 sep = "|",
                 encoding = "UTF-8")

meat_pig_mask=df["Item"]=="Meat, pig"
production_mask=df["Element"]=="Production"
producing_animal_mask=df["Element"]=="Producing Animals/Slaughtered"
non_zero_animal_mask=df[meat_pig_mask & producing_animal_mask,"Value"]==0

df_meat_pig<-data.frame()
df_meat_pig<-data.frame("Country" = df[meat_pig_mask & producing_animal_mask,"Area"],
                        "Meat per head" = df[meat_pig_mask & production_mask,"Value"]/df[meat_pig_mask & producing_animal_mask,"Value"])
#df_meat_pig[is.na(df_meat_pig)]<-0

#Read animal data
df <- read.table("data/GLEAM_Intake.csv", 
                 header = TRUE,
                 sep = ";",
                 encoding = "UTF-8")

swine_mask=df["Species"]=="Pigs"
production_system_mask=df["Production.system"]=="All systems"
herd_mask=df["Variable"]=="HERD: total number of animals"
grain_mask=df["Variable"]=="INTAKE: Total intake - Grains & Food crops"
grass_mask=df["Variable"]=="INTAKE: Total intake - Swill & Roughages"

swine_grain<-list()
swine_grass<-list()
for (country in df_meat_pig$Country) {
  country_mask=df["Country"]==country
  swine_grain<-c(swine_grain,df[swine_mask & production_system_mask & grain_mask & country_mask,"Value"][1]/df[swine_mask & production_system_mask & herd_mask & country_mask,"Value"][1])
  swine_grass<-c(swine_grass,df[swine_mask & production_system_mask & grass_mask & country_mask,"Value"][1]/df[swine_mask & production_system_mask & herd_mask & country_mask,"Value"][1])
}
swine_intake<-rbind(swine_grain,swine_grass)
swine_intake<-data.frame(swine_intake)
#swine_intake[is.na(swine_intake)]<-0
swine_intake<-t(swine_intake)
row.names(swine_intake) <- df_meat_pig$name

df_pig<-data.frame(cbind(df_meat_pig,swine_intake))
df_pig$swine_grain<-as.numeric(df_pig$swine_grain)
df_pig$swine_grass<-as.numeric(df_pig$swine_grass)

library(viridis)

mod <- lm(Meat.per.head ~ swine_grain, data=df_pig)
summary(mod)
par(mfrow = c(2, 2))
plot(mod)

df_pig$predlm[!is.na(df_pig$swine_grain)] <- predict(mod)


ggplot(df_pig,aes(x=swine_grain, y=Meat.per.head,color=swine_grass)) +
  geom_point(size=3) + 
  geom_line(aes(y = predlm), size = 1.5)+
  #labs(y="EF (kgCH4/head/year)", x = "Intake (kgDM/year)")+
  scale_color_viridis(option = "D",limits = c(0, 10))+
  theme(axis.title = element_text(size = 18),
        legend.text = element_text(size = 18),
        legend.title = element_text(face = "bold",size = 18))

coef_final<-data.frame(t(mod$coefficients))
colnames(coef_final)<- c("Intercept","Intake")
# coef_final[is.na(coef_final)] <- 0
write.csv(coef_final,'output/coefficients_weight_intake_swine_relation.csv')

con<-file('output/weight_intake_swine.csv',encoding="UTF-8")
write.csv(df_pig,con)

#Read emissions data
df <- read.table("data/FAOSTAT_manure_management.csv", 
                 header = TRUE,
                 sep = "|",
                 encoding = "UTF-8")

swine_mask=df["Item"]=="Swine"
stock_mask=df["Element"]=="Stocks"
emission_mask=df["Element"]=="Emissions (N2O) (Manure management)"

swine_emission<-list()
for (country in df_meat_pig$Country) {
  country_mask=df["Area"]==country
  swine_emission<-c(swine_emission,df[swine_mask & emission_mask & country_mask,"Value"][1]/df[swine_mask & stock_mask & country_mask,"Value"][1])
}

swine_emission<-data.frame(swine_emission)
swine_emission<-t(swine_emission)
row.names(swine_emission) <- df_pig$name

df_pig<-data.frame(cbind(df_pig,swine_emission))
df_pig$swine_emission<-as.numeric(df_pig$swine_emission)

mod <- lm(swine_emission ~ swine_grain, data=df_pig)
summary(mod)
par(mfrow = c(2, 2))
plot(mod)

df_pig$predlm[!is.na(df_pig$swine_grain)] <- predict(mod)


ggplot(df_pig,aes(x=swine_grain, y=swine_emission,color=swine_grass)) +
  geom_point(size=3) + 
  #geom_line(aes(y = predlm), size = 1.5)+
  #labs(y="EF (kgCH4/head/year)", x = "Intake (kgDM/year)")+
  scale_color_viridis(option = "D",limits = c(0, 10))+
  theme(axis.title = element_text(size = 18),
        legend.text = element_text(size = 18),
        legend.title = element_text(face = "bold",size = 18))

