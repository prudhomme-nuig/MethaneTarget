library(lme4)

df <- read.table("output/data_for_lm.csv", 
                 header = TRUE,
                 sep = ",",
                 encoding = "UTF-8")

df_temperate<-df#[df["GAEZ"]=="Temperate",]
mod_temparate <- lm(log(Milk_yield) ~ poly(Concentrate_intake,2,raw=TRUE) + factor (GAEZ), data=df_temperate)
#mod <- lm(Milk_yield ~ Concentrate_intake + Grass_intake, data=df_temperate)
summary(mod_temparate)
par(mfrow = c(2, 2))
plot(mod_temparate)
df_temperate$predlm <- predict(mod_temparate)

library(ggplot2)

df<-data.frame(seq(from = 0, to = 1.5, by = 0.01))
colnames(df)<-"x"
df["y"]<-data.frame(exp(coef_final[1,"Intercept"]+coef_final[1,"Concentrate_intake"]*df["x"]+coef_final[1,"Concentrate_intake_2"]*df["x"]^2))#+coef_final[1,"Tropical"]

ggplot(df,aes(x=x,y=y))+
  geom_line()+
  geom_point(data=df_temperate,aes(x = Concentrate_intake, y=Milk_yield))

ggplot(df_temperate,aes(x=Concentrate_intake, y=Milk_yield,color=factor(GAEZ),shape=factor(GAEZ))) +
  geom_point(size=3) + 
  geom_line(aes(y = exp(predlm)), size = 1.5)+
  #scale_color_discrete(name = "Grass intake:", labels = c("2 tDM/year", "3 tDM/year", "4 tDM/year"))+
  labs(y="Milk yield (t/year)", x = "Concentrate intake (tDM/year)")+
  theme(axis.title = element_text(size = 18),
        legend.text = element_text(size = 18),
        legend.title = element_text(face = "bold",size = 18))

# library(e1071)
# 
# saveRDS(mod_temparate, "output/milk_yield_concentrate.rds")
# file_conn <- file("output/milk_yield_concentrate.dep")
# writeLines(DEP_LIBS, file_conn)
# close(file_conn)

# df_tropical<-df[df["GAEZ"]=="Tropical",]
# mod_tropical <- lm(Milk_yield ~ poly(Concentrate_intake,2)  , data=df_tropical)
# #mod <- lm(Milk_yield ~ Concentrate_intake + Grass_intake, data=df_tropical)
# summary(mod_tropical)
# par(mfrow = c(2, 2))
# plot(mod_tropical)
# df_tropical$predlm <- predict(mod_tropical)
# 
# 
# ggplot(df_tropical,aes(x=Concentrate_intake, y=Milk_yield,color=factor(Grass_intake_cat))) +
#   geom_point(size=3) + 
#   geom_line(aes(y = predlm), size = 1.5)+
#   scale_color_discrete(name = "Grass intake:", labels = c("1 tDM/year", "2 tDM/year", "3 tDM/year"))+
#   labs(y="Milk yield (t/year)", x = "Concentrate intake (tDM/year)")+
#   theme(axis.title = element_text(size = 18),
#         legend.text = element_text(size = 18),
#         legend.title = element_text(face = "bold",size = 18))
# 
library("plyr")
coef_final<-data.frame(t(mod_temparate$coefficients))
colnames(coef_final)<- c("Intercept","Concentrate_intake","Concentrate_intake_2","Tropical")
# coef_final[is.na(coef_final)] <- 0
write.csv(coef_final,'output/coefficients_milk_yield_concentrate_relation.csv')
