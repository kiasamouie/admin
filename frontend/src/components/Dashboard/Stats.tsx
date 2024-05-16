"use client";
import React, { useEffect, useState } from "react";
import ChatCard from "../Chat/ChatCard";
import TableOne from "../Tables/TableOne";
import CardDataStats from "../CardDataStats";
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import useSWR from "swr";
import { fetcher } from "@/app/fetcher";
import { IconDefinition } from '@fortawesome/fontawesome-svg-core';
import { faClipboardList, faImage, faMusic } from '@fortawesome/free-solid-svg-icons';
import Loader from "@/components/common/Loader";;

type StatItem = {
  title: string;
  total: number;
  rate: string;
  levelUp?: boolean;
  levelDown?: boolean;
  icon: string;
};

const iconMap: { [key: string]: IconDefinition } = {
  faClipboardList: faClipboardList,
  faImage: faImage,
  faMusic: faMusic
};

const Stats: React.FC = () => {
  const { data: stats } = useSWR<StatItem[]>("/api/youtubedl/stats", fetcher);

  if (!stats) return <Loader visible={true} />;

  return (
    <>
      <div className="grid grid-cols-1 gap-4 md:grid-cols-2 md:gap-6 xl:grid-cols-4 2xl:gap-7.5">
        {stats.map((item, index) => (
          <CardDataStats
            key={index}
            title={item.title}
            total={item.total.toString()}
            rate={item.rate}
            levelUp={item.levelUp}
            levelDown={item.levelDown}
          >
            {iconMap[item.icon] && <FontAwesomeIcon icon={iconMap[item.icon]} className="text-primary dark:text-white" />}
          </CardDataStats>
        ))}
      </div>

      <div className="mt-4 grid grid-cols-12 gap-4 md:mt-6 md:gap-6 2xl:mt-7.5 2xl:gap-7.5">
        <div className="col-span-12 xl:col-span-8">
          <TableOne />
        </div>
        <ChatCard />
      </div>
    </>
  );
};

export default Stats;
