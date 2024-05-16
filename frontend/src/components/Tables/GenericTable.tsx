'use client';

import { BRAND } from "@/types/brand";
import Image from "next/image";
import useSWR from "swr";
import { fetcher } from "@/app/fetcher"

import { AuthActions } from "@/app/auth/utils";

const { handleJWTRefresh, storeToken, getToken } = AuthActions();

interface GenericTableProps {
  url: string;
}

const GenericTable: React.FC<GenericTableProps> = ({ url }) => {
  const { data: data } = useSWR(url, fetcher);
  const headers = data && data.length > 0 ? Object.keys(data[0]) : [];

  return (
    <div className="rounded-sm border border-stroke bg-white px-5 pb-2.5 pt-6 shadow-default dark:border-strokedark dark:bg-boxdark sm:px-7.5 xl:pb-1">
      <h4 className="mb-6 text-xl font-semibold text-black dark:text-white">
        Data Table
      </h4>

      <div className="flex flex-col">
        <div className="grid grid-cols-3 rounded-sm bg-gray-2 dark:bg-meta-4 sm:grid-cols-5">
          {headers.map((header, index) => (
            <div key={index} className="p-2.5 text-center xl:p-5">
              <h5 className="text-sm font-medium xsm:text-base">
                {header}
              </h5>
            </div>
          ))}
        </div>

        {data && data.map((item: any, rowIndex: number) => (
          <div
            className={`grid grid-cols-3 sm:grid-cols-5 ${
              rowIndex === data.length - 1
                ? ""
                : "border-b border-stroke dark:border-strokedark"
            }`}
            key={rowIndex}
          >
            {headers.map((header, colIndex) => (
              <div
                key={colIndex}
                className="flex items-center justify-center p-2.5 xl:p-5"
              >
                {Array.isArray(item[header]) ? (
                  item[header].map((subItem: any, subIndex: number) => (
                    <div key={subIndex}>
                      {typeof subItem === 'object'
                        ? JSON.stringify(subItem)
                        : subItem}
                    </div>
                  ))
                ) : typeof item[header] === 'object' && item[header] !== null ? (
                  JSON.stringify(item[header])
                ) : (
                  item[header]
                )}
              </div>
            ))}
          </div>
        ))}
      </div>
    </div>
  );
};

export default GenericTable;
