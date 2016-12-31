# Smoker Pi

So, this was pretty much an excuse to write some code and cook some meat... two of my favorite activities.

I bought a smoker a while back and used it several times with mixed results. It was cheap and it doubles as an electric grill which really works well. It's hard to beat something that is slow cooked all day but this smoker had no temperature control.

I ended up using a type K thermocouple (for the needed temperature tolerance) and a relay to control the smoker. The particular thermocouple that I used also requires an amplifier because the voltage changes across the thermocouple are so tiny. All of this together, allows the smoker to function like a thermostat and hover at the set temperature. Sure, I could just buy a more expensive smoker but this is way more fun... for now.

![setup](setup.jpg)

The hardware, combined with a bit of Python running on a Raspberry Pi allows me to SSH into my smoker and check the temperature inside the grill. There is just something about slow cooking something on a cold day that is very appealing. It is even more appealing to be able to check on things from inside using my phone.

Running the code is simple -- just give it your set temperature (in fahrenheit) and it will enter the control loop to maintain the set temperature.

    $ smoker.py --set-temp 250

The code also does some logging for later analysis. For, you know, science and stuff.

    1453661139,47.86,59.00,0,0
    1453661140,47.98,58.55,1,1
    1453661141,47.98,58.10,1,1
    1453661142,47.98,58.10,1,1
    1453661143,47.86,57.65,1,1
    1453661144,47.98,57.65,1,1
    1453661145,47.98,55.85,1,1
    1453661146,47.98,55.85,1,1
    1453661147,47.98,55.40,1,1
    1453661148,47.86,54.50,1,1

Here are the plots and the R code used to generate them.

![plot](plot.png)

![ambient](ambient.png)

    library(ggplot2)

    data = read.csv("smokelog_20160124-184539.csv", header=TRUE)
    data$date <- data$date - (5 * 3600)
    data$date <- ISOdatetime(1970,1,1,0,0,0) + data$date

    ggplot(data,aes(x = date,y = smoker_temp)) + 
      geom_point(aes(colour = smoker_temp)) +
      scale_colour_gradient2(low = "blue", mid = "green" , high = "red", midpoint = 16) + 
      geom_smooth(color = "grey30",size = 1) +
      scale_y_continuous(limits = c(50,300), breaks = seq(50,300,50)) +
      ggtitle ("Cooking Temperature") +
      xlab("Time") + ylab("Temperature (F)")

    ggplot(data,aes(x = date,y = ambient_temp)) + 
      xlab("Time") +
      ylab("Temperature (F)") +
      geom_point(aes(colour = ambient_temp)) +
      geom_smooth(color = "grey30",size = 1) +
      scale_y_continuous(limits = c(45,60), breaks = seq(45,60,5)) +
      ggtitle ("Ambient Temperature")

Finally, a shot of the hard earned result... It was awesome.

![meats](meats.jpg)

