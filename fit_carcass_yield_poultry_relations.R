library(lme4)
library(ggplot2)
library("plyr")

#Read activity data
df <- read.table("data/FAOSTAT_animal_yields.csv", 
                 header = TRUE,
                 sep = "|",
                 encoding = "UTF-8")

poultry_meat_mask=df["Item"]=="Meat, Poultry"
yield_mask=df["Element"]=="Production"
eggs_mask=df["Item"]=="Eggs Primary"
country_mask_tmp <- match(df[poultry_meat_mask & yield_mask,"Area"], df[eggs_mask & yield_mask,"Area"])
country_list<-df[eggs_mask & yield_mask,"Area"][country_mask_tmp]
country_mask<-df$Area %in% list(country_list)

df_poultry_meat<-data.frame()
df_poultry_meat<-data.frame("Country" = df[country_mask & eggs_mask & yield_mask,"Area"],
                        "poultry_meat" = df[poultry_meat_mask & yield_mask,"Value"],
                        "Eggs" = df[country_mask & eggs_mask & yield_mask,"Value"])
#df_poultry_meat[is.na(df_poultry_meat)]<-0

#Read emissions data
df <- read.table("data/GLEAM_Intake.csv", 
                 header = TRUE,
                 sep = ";",
                 encoding = "UTF-8")

poultry_mask=df["Species"]=="Chickens"
production_system_mask=df["Production.system"]=="All systems"
herd_mask=df["Variable"]=="HERD: total number of animals"
grain_mask=df["Variable"]=="INTAKE: Total intake - Grains & Food crops"
#by_products_mask=df["Variable"]=="INTAKE: Total intake - Agro-industrial by-products"

poultry_grain<-list()
poultry_by_product<-list()
for (country in df_poultry_meat$Country) {
  country_mask=df["Country"]==country
  poultry_grain<-c(poultry_grain,df[poultry_mask & production_system_mask & grain_mask & country_mask,"Value"][1]/df[poultry_mask & production_system_mask & herd_mask & country_mask,"Value"][1])
  poultry_by_product<-c(poultry_grain,df[poultry_mask & production_system_mask & by_products_mask & country_mask,"Value"][1]/df[poultry_mask & production_system_mask & herd_mask & country_mask,"Value"][1])
}
poultry_intake<-data.frame(poultry_grain)
#poultry_intake[is.na(poultry_intake)]<-0
poultry_intake<-t(poultry_intake)
row.names(poultry_intake) <- df_poultry_meat$name

df_poultry_meat<-data.frame(cbind(df_poultry_meat,poultry_intake))
df_poultry_meat$poultry_grain<-as.numeric(df_poultry_meat$poultry_intake)
#df_poultry_meat$poultry_grass<-as.numeric(df_poultry_meat$poultry_grass)

library(viridis)

mod <- lm(poultry_meat ~ poultry_intake, data=df_poultry_meat)
summary(mod)
par(mfrow = c(2, 2))
plot(mod)

df_poultry_meat$predlm[!is.na(df_poultry_meat$poultry_grain)] <- predict(mod)


ggplot(df_poultry_meat,aes(x=poultry_grain, y=poultry_meat)) +
  geom_point(size=3) + 
  geom_line(aes(y = predlm), size = 1.5)+
  #labs(y="EF (kgCH4/head/year)", x = "Intake (kgDM/year)")+
  scale_color_viridis(option = "D",limits = c(0, 2.5))+
  theme(axis.title = element_text(size = 18),
        legend.text = element_text(size = 18),
        legend.title = element_text(face = "bold",size = 18))

coef_final<-data.frame(t(mod$coefficients))
colnames(coef_final)<- c("Intercept","Intake")
# coef_final[is.na(coef_final)] <- 0
write.csv(coef_final,'output/coefficients_weight_intake_poultry_relation.csv')