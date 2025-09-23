import React, { useRef, useState } from "react";
import "bootstrap/dist/css/bootstrap.min.css";
import "bootstrap/dist/js/bootstrap.bundle.min.js";
import ReactPlayer from "react-player";
import { AiOutlineArrowDown } from "react-icons/ai";
import { Person } from "./person";

export const Home = () => {
  const ref = useRef(null);

  const handleClick = () => {
    ref.current.scrollIntoView({ behavior: "smooth" });
  };

  const [persons, setpersons] = useState([
    {
      image:
        "https://cdn.wisden.com/wp-content/uploads/2023/04/MS-Dhoni-980x530.png",
      name: "MS Dhoni",
      desc: "Former ICT captain, Csk captain",
      video: "https://www.youtube.com/watch?v=b4OH3vBANa4",
      word: "https://raw.githubusercontent.com/Caffeine-Coders/Sentiment-Analysis-Project/main/frontend/src/wordclouds/dhoniwordcloud.png",
    },
    {
      image:
        "https://openthemagazine.com/wp-content/uploads/2022/10/ViratKohli.jpg",
      name: "Virat Kohli",
      desc: "Indian Cricketers",
      video: "https://www.youtube.com/watch?v=gKw1zS5zU_I",
      word: "https://raw.githubusercontent.com/Caffeine-Coders/Sentiment-Analysis-Project/main/frontend/src/wordclouds/viratwordcloud.png",
    },
    {
      image:
        "https://images.unsplash.com/photo-1620083295363-2aef3e510a28?ixlib=rb-4.0.3&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=1770&q=80",
      name: "Trump",
      desc: "Former president of USA",
      video: "https://www.youtube.com/watch?v=54ShAhcxS4c",
      word: "https://raw.githubusercontent.com/Caffeine-Coders/Sentiment-Analysis-Project/main/frontend/src/wordclouds/trump%20data.png",
    },
    {
      image:
        "https://ca-times.brightspotcdn.com/dims4/default/d13f1be/2147483647/strip/true/crop/3000x2112+0+0/resize/1200x845!/quality/80/?url=https%3A%2F%2Fcalifornia-times-brightspot.s3.amazonaws.com%2F88%2Fd4%2Ffffe6e4c44baa85f9badc8bbe38d%2Famber-heard-75062.jpg",
      name: "Amber Heard",
      desc: "Actress",
      video: "https://www.youtube.com/watch?v=TqaRELRJcH4",
      word: "https://raw.githubusercontent.com/Caffeine-Coders/Sentiment-Analysis-Project/main/frontend/src/wordclouds/amberwordcloud.png",
    },
    {
      image:
        "https://people.com/thmb/YzxLyCRGNae_hm8ojS2S0pb4PGE=/1500x0/filters:no_upscale():max_bytes(150000):strip_icc():focal(749x0:751x2)/johnny-depp-1-29c4657afb7a4704ba1750de16b7283f.jpg",
      name: "Jhonny Depp",
      desc: "Actor",
      video: "https://www.youtube.com/watch?v=v9agVA_VeYE",
      word: "https://raw.githubusercontent.com/Caffeine-Coders/Sentiment-Analysis-Project/main/frontend/src/wordclouds/jhonny%20depp%20wordcloud.png",
    },
    {
      image:
        "https://ted-conferences-speaker-photos-production.s3.amazonaws.com/yoa4pm3vyerco6hqbhjxly3bf41d",
      name: "Bill Gates",
      desc: "Founder of Microsoft",
      video: "https://www.youtube.com/watch?v=6Af6b_wyiwI",
      word: "https://raw.githubusercontent.com/Caffeine-Coders/Sentiment-Analysis-Project/main/frontend/src/wordclouds/gateswordcloud.png",
    },
    {
      image:
        "https://upload.wikimedia.org/wikipedia/commons/e/e8/Mayor_Ed_Lee_Headshot_Closeup.jpg",
      name: "Ed Lee",
      desc: "Mayor of SF",
      video: "https://www.youtube.com/watch?v=he8hGWEg298",
      word: "https://raw.githubusercontent.com/Caffeine-Coders/Sentiment-Analysis-Project/main/frontend/src/wordclouds/edlee%20wordcloud.png",
    },
    {
      image:
        "https://upload.wikimedia.org/wikipedia/commons/thumb/3/34/Elon_Musk_Royal_Society_%28crop2%29.jpg/1200px-Elon_Musk_Royal_Society_%28crop2%29.jpg",
      name: "Elon Musk",
      desc: "Current CEO of Twitter",
      video: "https://www.youtube.com/watch?v=sQIx6YeMRR8",
      word: "https://raw.githubusercontent.com/Caffeine-Coders/Sentiment-Analysis-Project/main/frontend/src/wordclouds/elonwordcloud.png",
    },
    {
      image:
        "https://s.abcnews.com/images/Politics/EPA_Clinton_Trump_Split_jrl_161024_16x9_1600.jpg",
      name: "Hilary Clinton vs Trump",
      desc: "Polictical Rivals",
      video: "https://www.youtube.com/watch?v=DBhrSdjePkk",
      word: "https://raw.githubusercontent.com/Caffeine-Coders/Sentiment-Analysis-Project/main/frontend/src/wordclouds/HvsTwordcloud.png",
    },
    {
      image:
        "https://media.glamour.com/photos/6259bf450e99bcd975ad0a1e/master/w_2560%2Cc_limit/1391651723",
      name: "Meghan Markle",
      desc: "Former Royal of UK",
      video: "https://www.youtube.com/watch?v=1hhsvnV5CIc",
      word: "https://raw.githubusercontent.com/Caffeine-Coders/Sentiment-Analysis-Project/main/frontend/src/wordclouds/meghan%20word%20cloud.png",
    },
    {
      image:
        "https://hips.hearstapps.com/hmg-prod/images/oprah-winfrey-arrives-at-the-premiere-of-owns-david-makes-news-photo-1678107172.jpg",
      name: "Oprah Winfrey",
      desc: "TV host",
      video: "https://www.youtube.com/watch?v=Fo6oU4DfdH0",
      word: "https://raw.githubusercontent.com/Caffeine-Coders/Sentiment-Analysis-Project/main/frontend/src/wordclouds/oprahwordcloud.png",
    },
    {
      image:
        "https://s.yimg.com/ny/api/res/1.2/Tl6Wc4vo09U9wCog3BkLHQ--/YXBwaWQ9aGlnaGxhbmRlcjt3PTk2MDtoPTY0MA--/https://media.zenfs.com/en/people_218/ceb39adca9cb11facd5b338cba8f9c25",
      name: "Jhonny Depp vs Amber Heard",
      desc: "The Trail Tweets",
      video: "https://www.youtube.com/watch?v=aGEzD_zFE2I",
      word: "https://raw.githubusercontent.com/Caffeine-Coders/Sentiment-Analysis-Project/main/frontend/src/wordclouds/trailwordcloud.png",
    },
    {
      image:
        "https://www.gannett-cdn.com/-mm-/13e91021ee7e2fe7c62a54fe4ec9f15d9f63fecc/c=0-0-2996-1693/local/-/media/2018/05/21/USATODAY/USATODAY/636625026301850918-NUP-180738-0242.JPG?width=2996&height=1693&fit=crop&format=pjpg&auto=webp",
      name: "Jimmy Fallon",
      desc: "TV Host",
      video: "https://www.youtube.com/watch?v=-6v7iDCPJWU",
      word: "https://raw.githubusercontent.com/Caffeine-Coders/Sentiment-Analysis-Project/main/frontend/src/wordclouds/jimmywordcloud.png",
    },
    {
      image:
        "https://m.economictimes.com/thumb/msid-71255941,width-1200,height-900,resizemode-4,imgsize-955580/howdy-modi-triumphant-moment-for-indo-us-ties-usispf.jpg",
      name: "Narendra Modi",
      desc: "Opinion about the Indian Politician",
      video: "https://www.youtube.com/watch?v=VYZUkTm4E-0",
      word: "https://raw.githubusercontent.com/Caffeine-Coders/Sentiment-Analysis-Project/main/frontend/src/wordclouds/modiwordcloud.png",
    },
    {
      image:
        "https://upload.wikimedia.org/wikipedia/commons/0/0b/Arvind_Kejriwal_smiling_%28cropped%29.jpg",
      name: "Kejriwal",
      desc: "Indian Politician",
      video: "https://www.youtube.com/watch?v=ymseMeGVfJE",
      word: "https://raw.githubusercontent.com/Caffeine-Coders/Sentiment-Analysis-Project/main/frontend/src/wordclouds/kejrival.png",
    },
    {
      image:
        "https://www.deccanherald.com/sites/dh/files/articleimages/2023/01/01/nm-1177027-1672590352.jpg",
      name: "Narendra Modi",
      desc: "Indian Politician",
      video: "https://www.youtube.com/watch?v=VYZUkTm4E-0",
      word: "https://raw.githubusercontent.com/Caffeine-Coders/Sentiment-Analysis-Project/main/frontend/src/wordclouds/modi2%20wordcloud.png",
    },
    {
      image:
        "https://hips.hearstapps.com/hmg-prod/images/gettyimages-1239961811.jpg?crop=1.00xw:1.00xh;0,0&resize=1200:*",
      name: "Barack Obama",
      desc: "American Politician",
      video: "https://www.youtube.com/watch?v=nEEtBVPiI44",
      word: "https://raw.githubusercontent.com/Caffeine-Coders/Sentiment-Analysis-Project/main/frontend/src/wordclouds/obamawordcloud.png",
    },
    {
      image:
        "https://localist-images.azureedge.net/photos/36023435672136/original/361b47ffab5364f3368fe18de8e67e93768dd7bf.jpg",
      name: "Rahul Gandhi",
      desc: "Indian Politician",
      video: "https://www.youtube.com/watch?v=1x1eQQPkTjc",
      word: "https://raw.githubusercontent.com/Caffeine-Coders/Sentiment-Analysis-Project/main/frontend/src/wordclouds/rahul%20gandhiwordcloud.png",
    },
  ]);
  const [topics, settopics] = useState([
    {
      image:
        "https://pixelz.cc/wp-content/uploads/2018/07/nasa-logo-uhd-4k-wallpaper.jpg",
      name: "NASA",
      desc: "National Aeronautics and Space Administration",
      video: "https://www.youtube.com/watch?v=WeA7edXsU40",
      word: "https://raw.githubusercontent.com/Caffeine-Coders/Sentiment-Analysis-Project/main/frontend/src/wordclouds/nasawordcloud.png",
    },
    {
      image:
        "https://cloudfront-us-east-2.images.arcpublishing.com/reuters/AZ3C2MC6TFISFPLH23LDWY2B74.jpg",
      name: "ChatGPT",
      desc: "Artificial Intelligence Chatbot",
      video: "https://www.youtube.com/watch?v=eg9qDjws_bU",
      word: "https://raw.githubusercontent.com/Caffeine-Coders/Sentiment-Analysis-Project/main/frontend/src/wordclouds/chatgptwordcloud.png",
    },
    {
      image:
        "https://cdn.britannica.com/67/237867-131-EFFE4CE2/Elephant-symbol-Republican-Party-Donkey-symbol-Democratic-Party.jpg",
      name: "Democratic vs Republicans",
      desc: "2 Major contemporary political parties in the US",
      video: "https://www.youtube.com/watch?v=Z5cLtd0cxfo",
      word: "https://raw.githubusercontent.com/Caffeine-Coders/Sentiment-Analysis-Project/main/frontend/src/wordclouds/demovsrepwordcloud.png",
    },
    {
      image:
        "https://www.aljazeera.com/wp-content/uploads/2020/11/2020-11-09T114528Z_401439984_RC2NZJ9UB98H_RTRMADP_3_HEALTH-CORONAVIRUS-VACCINES-PFIZER.jpg?resize=1920%2C1440",
      name: "Pfizer",
      desc: "Covid 19 Vaccine",
      video: "https://www.youtube.com/watch?v=LjZMgtzG6dE",
      word: "https://raw.githubusercontent.com/Caffeine-Coders/Sentiment-Analysis-Project/main/frontend/src/wordclouds/pfizerwordcloud.png",
    },
    {
      image:
        "https://www.nycclc.org/sites/default/files/primary-photos/news/covid-19-pandemic-resources-december-23-2020-covid-19.png",
      name: "Covid 19",
      desc: "Corona Virus - A Pandemic",
      video: "https://www.youtube.com/watch?v=N23xJidPMeQ",
      word: "https://raw.githubusercontent.com/Caffeine-Coders/Sentiment-Analysis-Project/main/frontend/src/wordclouds/covidwordcloud.png",
    },
    {
      image: "https://w0.peakpx.com/wallpaper/503/2/HD-wallpaper-nasa-logo.jpg",
      name: "NASA - older version",
      desc: "National Aeronautics and Space Administration",
      video: "https://www.youtube.com/watch?v=WeA7edXsU40",
      word: "https://raw.githubusercontent.com/Caffeine-Coders/Sentiment-Analysis-Project/main/frontend/src/wordclouds/nasa1wordcloud.png",
    },
  ]);

  const [entertainment, setentertainment] = useState([
    {
      image:
        "https://hindubabynames.info/downloads/wp-content/themes/hbn_download/download/sports-ipl/ipl-logo.png",
      name: "IPL 2022",
      desc: "Worlds most popular cricket league hosted in India",
      video: "https://www.youtube.com/watch?v=CyWG55DX2E4",
      word: "https://raw.githubusercontent.com/Caffeine-Coders/Sentiment-Analysis-Project/main/frontend/src/wordclouds/ipl2022.png",
    },
    {
      image:
        "https://static.vecteezy.com/system/resources/previews/009/567/499/original/fifa-logo-fifa-world-cup-free-vector.jpg",
      name: "FIFA",
      desc: "It is the Worlds most popular League",
      video: "https://www.youtube.com/watch?v=RjRs3Y2UXTY",
      word: "https://raw.githubusercontent.com/Caffeine-Coders/Sentiment-Analysis-Project/main/frontend/src/wordclouds/fifa%20word%20cloud.png",
    },
    {
      image:
        "https://www.shutterstock.com/image-vector/illustration-batsman-playing-cricket-india-260nw-1420671143.jpg",
      name: "IndvsPak Cricket Rivalry",
      desc: "It is the El- Classico of Cricket",
      video: "https://www.youtube.com/watch?v=cXxfvdVFt58",
      word: "https://raw.githubusercontent.com/Caffeine-Coders/Sentiment-Analysis-Project/main/frontend/src/wordclouds/IndvsPakwordcloud.png",
    },
    {
      image: "https://assets.stickpng.com/images/58428defa6515b1e0ad75ab4.png",
      name: "NBA",
      desc: "One of the most famous Basketball League around the world",
      video: "https://www.youtube.com/watch?v=dxbVdyVYGcQ",
      word: "https://raw.githubusercontent.com/Caffeine-Coders/Sentiment-Analysis-Project/main/frontend/src/wordclouds/nba.png",
    },
    {
      image:
        "https://logolook.net/wp-content/uploads/2021/07/Avengers-Log%D0%BE.png",
      name: "Avengers",
      desc: "Avengers - it is a movie released in 2014 by Marvel",
      video: "https://www.youtube.com/watch?v=PhAsdlmY0o8",
      word: "https://raw.githubusercontent.com/Caffeine-Coders/Sentiment-Analysis-Project/main/frontend/src/wordclouds/avenger.png",
    },
    {
      image:
        "https://cdn.theatlantic.com/thumbor/4xedENNyVDQrfV_-6NrWA2wnfJo=/0x0:1600x900/1600x900/media/img/mt/2018/07/TDK/original.jpg",
      name: "DarkKnight",
      desc: "Dark Knight- it is a movie released by DC",
      video: "https://www.youtube.com/watch?v=TsLEolNcXug",
      word: "https://raw.githubusercontent.com/Caffeine-Coders/Sentiment-Analysis-Project/main/frontend/src/wordclouds/darknightwordcloud.png",
    },
    {
      image:
        "https://i0.wp.com/batman-news.com/wp-content/uploads/2019/08/Joker-Official-Images-Final-Poster-1600-Featured-01.jpg?fit=1600%2C900&quality=80&strip=info&ssl=1",
      name: "Joker",
      desc: "a Psychological movie",
      video: "https://www.youtube.com/watch?v=ofIa6cbeV9w",
      word: "https://raw.githubusercontent.com/Caffeine-Coders/Sentiment-Analysis-Project/main/frontend/src/wordclouds/joker%20word%20cloud.png",
    },
    {
      image:
        "https://w0.peakpx.com/wallpaper/99/136/HD-wallpaper-movie-john-wick-chapter-3-parabellum-john-wick-keanu-reeves.jpg",
      name: "John Wick",
      desc: "Man of sheer will",
      video: "https://www.youtube.com/watch?v=zlf2l9HoImk",
      word: "https://raw.githubusercontent.com/Caffeine-Coders/Sentiment-Analysis-Project/main/frontend/src/wordclouds/jhonwickwordcloud.png",
    },
    {
      image:
        "https://www.filmyfenil.com/wp-content/uploads/2019/06/Kabir-Singh-wallpaper.jpg",
      name: "Kabir Singh",
      desc: "It is a bollywood movie",
      video: "https://www.youtube.com/watch?v=RiANSSgCuJk",
      word: "https://raw.githubusercontent.com/Caffeine-Coders/Sentiment-Analysis-Project/main/frontend/src/wordclouds/kabir%20singh%20word%20cloud.png",
    },
    {
      image: "https://images8.alphacoders.com/128/1282650.jpg",
      name: "Morbius",
      desc: "Movie released by Sony under MCU",
      video: "https://www.youtube.com/watch?v=MAXU4dMOBLk",
      word: "https://raw.githubusercontent.com/Caffeine-Coders/Sentiment-Analysis-Project/main/frontend/src/wordclouds/morbiuswordcloud.png",
    },
    {
      image: "https://cdn.marvel.com/content/1x/maguiregarfieldholland_opt.jpg",
      name: "SpiderMan No Way Home",
      desc: "Movie released by Sony under MCU",
      video: "https://www.youtube.com/watch?v=8CQ-SNNBvyQ",
      word: "https://raw.githubusercontent.com/Caffeine-Coders/Sentiment-Analysis-Project/main/frontend/src/wordclouds/spidermannowaywordcloud.png",
    },
  ]);

  const [currdiv, setcurrdiv] = useState(0);

  return (
    <div className="Home">
      {/* <Nav /> */}
      <div className="video">
        {/* <ReactPlayer
          url={video}
          playing={true}
          width="100%"
          height="100%"
          // volume={0.8}
          muted={true}
          loop={true}
        /> */}
        <button className="play-button" onClick={handleClick}>
          Scroll-down <AiOutlineArrowDown />
        </button>
      </div>

      <div ref={ref}>
        <Person persons={persons} />
        <Person persons={topics} />
        <Person persons={entertainment} />
      </div>
    </div>
  );
};
