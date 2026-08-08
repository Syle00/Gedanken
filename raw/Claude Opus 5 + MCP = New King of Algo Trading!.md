---
title: "Claude Opus 5 + MCP = New King of Algo Trading!"
source: "https://www.youtube.com/watch?v=Dbof8VUxP9E&t=426s"
author:
  - "[[Algo-trading with Saleh]]"
published: 2026-07-25
created: 2026-08-08
description: "Claude Opus 5 takes on a complete algo-trading challenge: researching and building an ETH/USDT trend-following strategy with Jesse MCP. I test how well it writes Python strategy code, runs backtests a"
tags:
  - "clippings"
---
![](https://www.youtube.com/watch?v=Dbof8VUxP9E)

Claude Opus 5 takes on a complete algo-trading challenge: researching and building an ETH/USDT trend-following strategy with Jesse MCP. I test how well it writes Python strategy code, runs backtests and parameter optimization, validates statistical significance, and uses Monte Carlo simulations to check for overfitting. We also review the final strategy's multi-year performance, interactive trade chart, and source code.  
  
00:00 Claude Opus 5 Overview  
01:17 Jesse MCP Setup  
02:46 The Strategy Research Prompt  
04:17 Opus 5 Research Results  
06:01 Backtest Results and Metrics  
08:17 Multi-Year Strategy Performance  
11:55 Interactive Trade Chart  
14:03 Significance and Monte Carlo  
15:52 Strategy Report and Code  
19:38 Final Strategy and Download  
  
👉 Get the exact ETHSTPullback30m strategy from this video:  
https://jesse.trade/strategies/ethstpullback30m?utm\_source=opus-5  
  
👉 Follow our Telegram channel:  
https://jesse.trade/telegram  
  
👉 Join our FREE Discord community:  
https://jesse.trade/discord  
  
👉 Apex signup URL for 25% fee discounts:  
https://jesse.trade/apex  
  
👉 KuCoin signup URL for a 15% trading fee discount:  
https://jesse.trade/kucoin  
  
👉 Explore my other strategies:  
https://jesse.trade/strategies?utm\_source=opus-5

## Transcript

### Claude Opus 5 Overview

**0:00** · The Anthropic team just released Claude Opus 5, and this is huge, guys, because this model is beating Fable 5 while costing significantly less. In fact, even on a $200 max subscription of Anthropic, I was not really able to use Fable 5 as much as I needed. Whenever I ran a task for like 30 minutes to 1 hour, it would drain my usage very quickly. But with Opus 5, I can get the same quality for a significantly cheaper price. And look at this benchmark.

**0:28** · Like, it's beating it in agenting terminal coding, knowledge work, which is also important for us because imagine if you want to come up with some sort of trading strategy idea, this model is going to be able to help you better with that. It's also scoring 30% for novel problem solving, which is absolutely crazy because even GPT-5.1.6 solved, which was my favorite model until yesterday, is a scoring 7.8%. So, this is crazy, guys.

**0:54** · So, in this video, as always, I'm going to be testing the model to see how good it is for writing strategies, running back tests, parameter optimizations, and Monte Carlo simulations to ensure not only it finds us good strategies, but also it ensures they are not overfit. Before I move on, I got to mention I am not a financial advisor, and this video is for educational purposes only. So, guys, let's get started. As always, I'll be using the Jesse framework for the algo trading side of things using Python.

### Jesse MCP Setup

**1:24** · It's absolutely free to get started with, and you can follow the documentation to get it installed on your machine. And if you prefer videos, I also have those on my channel. So, just go ahead and get started with that.

**1:35** · And assuming you've already done that, all I need to do to get started is to run the Jesse run command. There we go.

**1:42** · This is the address for the dashboard, and this is the address for the MCP. So, let's copy this. Now, in order to run Claude code, we're going to have to run it inside another terminal. And because I'm on the Z editor, it allows us to do it right from here. Now, this is another terminal, very similar to this one, but it is on the sidebar. So, I could just run the Claude command in order to run Claude code on my terminal right now, but if you haven't added Jesse MCP into Claude, you need to do it using this command that is on the documentation of Jesse.

**2:13** · And you notice the address that I copied was running on the port 9007. So, instead of 9002, I have to enter that.

**2:20** · But for you, this is going to be the default value. So, just go ahead, copy this and run it here, and you should be good to go. I've already done this, so I'm not going to do that. I will just instead run the Claude command. There we go. Now, to ensure that I'm running on the Opus 5, I'm going to run the /model command, and here you can see that the default is now using Opus 5. And the effort is set to high, which I find it to be more than enough for my use case.

### The Strategy Research Prompt

**2:46** · All right, next we're going to have to feed the prompt to the model. And in case if you just want to copy and paste it, I'm going to put it on GitHub and link to the repository in the description of the video. So, let's get started. Hey there, I need you to do research and develop a trend following strategy for trading ETH USDT that enters on pullbacks within an established trend. Use supertrend as the primary indicator, supported by an EMA-based trend filter, and any other confirmation indicator you see fit.

**3:13** · Use the 30-minute time frame as the main trading time frame, and the 4 hours as the anchor time frame. I need the results of it to be good since the beginning of the year until now. And when I say good, I mean a sharp ratio of at least 1.5. Risk 3% of the account per each trade. Every time you develop a strategy, validate the result using a statistical significance test before writing the full strategy to ensure the entry rules are not pure noise.

**3:40** · Only proceed if the strategy's metrics demonstrate genuine statistical significance. Feel free to use optimization to improve the results. At the end, apply Monte Carlo simulations to ensure the results are not overfit.

**3:55** · Continue until you find strategies that fully meet the criteria requested. Do not prompt me in the meanwhile. Good luck. There we go. Let's hit enter. This seems fine. And as you can see, it's started reading the agents.to.them.defile of the project, which is going to tell it to use J S MCP in order to write the strategy and do the research. So, let's go and come back a bit later. All right, so it did it everything that I needed to do and it performed it very quickly. So, I basically just went for lunch, I came back and it was ready. And as you can see, it's also very verbose.

### Opus 5 Research Results

**4:26** · And this is helpful if you are a beginner. So, for example, you can see exactly the path that the AI is taking in order to develop the strategy. And especially for beginners, that is super helpful because you want to learn. So, the first thing that it did is that once it wrote the strategy, it ran an RST test, which is rule significance test, which it allows us to know whether the entry rules of the strategy were pure noise or luck or was there an actual edge in it.

**4:55** · So, it does that before moving on with the rest of the strategy such as the position sizing, take profit and a stop loss.

**5:04** · Because if the entry rules of the strategy don't have an actual edge, then everything else that we do is pointless.

**5:09** · So, it did that to validate the results that it found and then it continued until it found a good strategy.

**5:16** · Here we can see it says version four is profitable, which means it wrote four versions until this point. There's another V5. So, it tried out many different variations of the same strategy until at this point it was able to find the ending result that we wanted. So, a sharp ratio of 1.68, net profit of 30%, a max drawdown of minus 17% and it executed 48 trades. So, this looks good and it gave me URLs for the final backtest, the RST test and the Monte Carlo so we can check it out.

**5:46** · But, before I move on, I also asked the model to do something else. I needed to add charts to the strategy so that we can visualize it better. And that's literally what I told it. But, now that I'm thinking, it would probably be better if I added this to the prompt that I gave the model in the first place. So, let's just scroll down, and here's the backtest results for what we asked, and it also went ahead and tested with other periods, such as this one, which is for 2 and 1/2 year, and this one is for 5 and 1/2 years.

### Backtest Results and Metrics

**6:13** · And of course, these are super helpful if you want to use the strategy to go live with it. So, let's open this one first. Now, one problem I have with it is that this format that it is printing this, it doesn't work. Okay, if I click on this, we're going to get an error because this ID is not complete. We also need this one. So, let's ask it to fix this.

**6:34** · Please give me new URLs for everything, not just the backtest, and also ensure the URLs are on one line so I can just click on it because the format that you just printed them in a table doesn't work. Now, while that's going, I want to quickly remind you guys about our Telegram. It's the fastest way to get notified about my future work, whether it's a new tutorial or a tool that I create. Also, don't forget to check out our free Discord, where more than 5,000 members like you and I are hanging out there and helping out each other with algo trading so we can all succeed together. The links for both are down in the description. All right, there we go.

**7:07** · So, let's open this one and also this one and this. So, there we go. This is the result of the backtest from the beginning of the year until this month.

**7:16** · Now, if you see the dashboard being different, that's because I'm running version three of Jesse, which hasn't been released yet, but it is coming in the coming days. I have basically redesigned everything and made everything better. But anyways, here's the equity chart, and this indigo equity curve is the one for a strategy's performance, and this one in orange is the performance of ETH/USDT if you were just buying and holding the asset. And here's the chart for the worst five drawdown periods, and as you can see, it's not looking great.

**7:43** · Like short, this is awesome, and so is this one, but we had a nasty drawdown period in here, and this is the monthly return chart. It executed 48 trades, the net profit is 30%, the max drawdown is -17, the win rate is 31%, but the average win to loss is really huge, so it is 3.8. The average holding time is 38 hours, the Sharpe ratio is 1.68, which is way above 1.5 criteria that we set for the model.

**8:12** · And the average trades per month is seven. So, overall, looking really good, and the model was kind enough to also execute it on other periods. So, this one is for 2 and 1/2 year, and it actually looks really good. So, here's the equity curve chart, and as you can see, it's going up nice and steady while the actual underlying asset, which is ETH, is in a range market. So, if you were just holding ETH, you would not have made a lot of money, but with this, it would have been much better.

### Multi-Year Strategy Performance

**8:37** · The max drawdown is still -17%, the win rate is 27%, but the average win to loss ratio is 3.95.

**8:47** · So, guys, a strategy like this is very difficult to trade mentally. So, from a psychology side, most of us are not going to be able to continue trading something like this, because basically every seven out of 10 trades that you take are going to be losing ones. And the Sharpe ratio is 1.35, which is still good. And the average trades per month is eight. So, overall, this is looking really good. And the chart for the worst five drawdown periods is also looking better now.

**9:14** · So, you see, guys, zooming out is always the key, because in the end, we're not going to be trading just one strategy, right? So, even for this period, for example, which is multiple months, and the strategy wasn't doing fine, if you can develop another strategy which isn't super correlated to this one, and if that one was doing fine during this period, then we we have been fine, because the other strategy was making money while this one was in a range. And when you execute multiple strategies like this simultaneously, you're going to get a better sharp ratio and even a better max drawdown.

**9:44** · So, that is something to remember that do not expect to just trade one strategy in the end. Anyways, moving on, here's the chart for the monthly returns of it and as you can see, every year it is profitable and in most months we are also green, but not in all of them. And we have months as bad as minus 11%. We also have good ones as good as 17%.

**10:07** · Next, let's take a look at the results for the 5 and 1/2 years of backtest and as you can see, it still looks good even though there are periods such as this one where it was totally in a range. So, the strategy's results wasn't super awesome, but it wasn't that bad either.

**10:23** · So, it's not like it was falling a lot.

**10:25** · We also had a bad period here. So, even though the price was going up, the strategy wasn't performing well and we were actually in a loss. So, this is very important to remember that a strategy like this could even lose money in the short term even when the market is going up and that is going to be very difficult mentally. So, if I were trading this strategy at this period, I would have probably stopped and would have lost on these profits over the next few years.

**10:49** · So, this is also really important and another reason for why you guys need a portfolio of strategies instead of just trading one because it's going to be a lot easier mentally if you had other strategies running in this period and you weren't allocating all of your capital to just one single strategy. Anyways, here's the drawdown chart and this one was not only the worst one, it was also the longest one.

**11:14** · And in fact, we can actually see how long that was by taking a look at this.

**11:18** · So, max underwater period was 205 days.

**11:22** · So, close to a year. So, this was very brutal if you were trading it during that period. Anyways, so the max drawdown is minus 20% which is a good number. The total number of trades is 541.

**11:34** · The P&amp;L would have been 607%.

**11:37** · The win rate was 28%. The sharp ratio was 1.34. And the average trades per month was eight. So, overall, I really like this result. Even though so far I just spent like an hour developing it with this AI model. So, of course, I'm going to keep working on it. But even as it is, it does have a lot of potential.

### Interactive Trade Chart

**11:56** · Now, one more thing I want to show you guys. Remember when I asked the model to add charts to it. So, because I did that, here I can click on the trade chart button here and it's going to show me an interactive chart which allows us to see every single trade that it took.

**12:11** · So, for example, let's sort it based on the best ones. And this one presumably made 45%, right? So, let's click on it and zoom in a little bit. So, we can see exactly where it opened and where it closed, right? But these indicator values, these are the ones that we asked it to add. So, here we can see the regime, for example. So, when was it minus one? So, these were ready for a short position. And this was zero, so a neutral territory as you can also see the label here. But I want to minimize this one to have more place for this.

**12:42** · And we also have the ADX, but I also want to minimize this one. And here we can see this blue line here is the 4-hour EMA 200, which is the strategy it's using. So, let's also toggle this.

**12:54** · And this orange one is the super trend for the 4-hour time frame. So, let's toggle this one also. And this red line here is the stop loss. So, let's also toggle this one. So, that is only going to leave us with this purple line, which is the super trend value on the 30-minutes time frame. So, let's zoom in a little bit. Next, I'm going to go click on here. So, now we can see it went short here. And let's zoom out a little bit. There we go.

**13:19** · And if I hold the mouse here again, we can see exactly where where opened the trade and where it closed it. So, let's also click on this one, another one. Now, we can also sort it based on the worst ones. So, this one it lost 12%. Now, by the way, this isn't 12% of your entire capital, of course, because we were only risking 2% of the capital per each trade. So, this cannot be more than that, of course, but this is just based on the the price movement.

**13:46** · So, I wouldn't really look at this or care about it a lot, but anyway, so let's just click here. So, here we can see a losing trade. So, let's zoom in. So, we went short here, but the price actually went up. Let's see another one and also another one. All right, going back to the terminal where we had the cloud code, we can also see the results for the significance test, for example. So, let's give this one a try. There we go. So, here's the chart.

### Significance and Monte Carlo

**14:12** · Because the P value is lower than this value here, we're going to say the entry rules of the strategy has statistical significance. So, I am a little bit over simplifying this because explaining how this algorithm works requires its own video, but basically, this is all you need. So, if the results is saying that it is significantly significant, that's it. Just move on to the other parts of the strategy.

**14:34** · And last, but definitely not least, the Monte Carlo simulation is the most important piece of the puzzle because sure, we got these results and they were good, but you want to ensure that it isn't overfit. And as you can see in the chart, the orange line is the original backtest equity curve, and we can see that it is ending in right in the middle. And the simulations are way above it.

**14:55** · So, this is a really good sign because if this one, for example, was just here, like way at the top, it would have been a clear sign that we were just being lucky during those backtests, which is not a good sign if you want to take the strategy live. And if you also read this table here, we can see the Sharpe ratio of the original was 1.62, but the median number is 1.93, and the best 5% is 4.36. So, usually, I want the original back test sharp ratio to be near median.

**15:25** · So, something such as two or even 2.4 maybe, that would have been fine for me. So, I would have said that that is not overfit. But, as you can see, this case is even less than the median number. So, this is a very good sign and maybe, just maybe, this is also the same reason why it's performing so well during the bigger periods. Now, I'm going to move on, but if you guys want to take this strategy live, I also suggest try Monte Carlo simulations on these bigger periods. Now, we can also see that the agent wrote us a complete report file in the markdown format.

### Strategy Report and Code

**15:56** · So, we can see what was the strategy's name and what was the parameters that it used, what was the target that it achieved, and how it did it. It also gives us a pretty good summary of everything that just went on. Now, let's also take a look at the strategy's code.

**16:12** · So, we can see a really huge section of the explanation. We can just skip all of it. Here's the percentage that it risk per each trade. It defined the anchor time frame, which is always a good idea for determining the bigger trend of the market and the ATR indicator. It also wrote some useful comments such as this one, data and signal. We can see the anchor regime, which I'm guessing is the bigger trend, and it is using the super trend, and it is passing the anchored candle. So, pretty standard stuff.

**16:40** · It is also using the before method of Jesse in order to store some variables to use later. Now, I don't think this is exactly the best syntax. I think it wrote things a little bit more complicated than what I personally would have, but it is fine. So, moving on, it also defined another method called the entry signal, which is responsible to tell us whether we want to open a long or a short position. And then, inside the should long and should short methods of Jesse, it is simply returning the value of this signal.

**17:13** · So, it's saying that if it's one, we want to go long. If it's minus one, we want to go short.

**17:19** · However, this is actually a pretty good syntax because it is just making the decision if you want to open a long or short position, but it's not actually executing the orders. Next, inside the go long and go short methods of Jesse, we can see it's defining the entry order, which is being the current price, the stop loss order, and it is also storing the stop loss order so that we can use it later, and it is submitting the buy and the sell orders with this syntax.

**17:45** · Now, because the results are good, I'm going to give it a pass, but in the actual prompt that we gave the agent, I did not want it to open the positions using market orders, and that is why I said that I want to go long during a pullback. So, what I meant by a pullback was entering via a limit order.

**18:03** · Now, maybe I should have been more specific with it, but this isn't exactly what I had in mind. But anyways, moving on. So, once it opens the position, it is submitting the stop loss order, and that is was storing the sub price here.

**18:17** · So, this is also good. And notice that it did not define a take profit order, and instead it's using the update position method of Jesse, which is executed after every single candle closes to keep updating the stop loss order, and also saying that if the regime is no longer with us, we want to liquidate the current position. So, basically, this is using a trailing a stop kind of take profit, which is pretty a standard if you want to take the most out of a trend.

**18:45** · And I'm guessing this is why the average win to loss ratio of the strategy was so high while the win rate was low. And finally, we have the update chart method of Jesse, which is actually new inside the version three, which isn't released yet.

**19:01** · Again, it's coming in the coming days.

**19:03** · What it does is that it adds some indicators to the chart so we can view it inside the interactive chart. Now, we actually had this feature before, but this one is just the upgraded version of that and it also works during live trading. So, not just the back test, which is the limitation that we had before. But anyways, moving on, we also have the upper parameters, which is defined, such as the stop ATR, trailing ATR, the ADX mean, which is for the threshold of the ADX and things like that.

**19:30** · So, this is the syntax that we use inside the JSE framework in order to run optimization to find the best parameters. As always, I did submit this strategy on our strategies index page on our website. So, if you want to check it out on other trading periods and see the metrics for those, you can check out this page and I'm going to link to it in the description of the video. You can also check out this page for other strategies submitted either by me or other members of our community. I forgot to mention you can also download the source code of the strategy by clicking here.

### Final Strategy and Download

**20:00** · Anyways, if you enjoyed the video, please make sure to give it a like and post a comment to let me know what you think. It helps me out a lot and don't forget to subscribe if you haven't already because I will be creating more videos just like this one in the future.

**20:13** · Thank you so much for watching. I'll see you in the next one.

**20:18** · \[music\]