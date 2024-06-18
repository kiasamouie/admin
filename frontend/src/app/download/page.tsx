'use client';

import React, { useState, useEffect } from "react";
import { useForm } from "react-hook-form";
import Link from "next/link";
import Image from "next/image";
import Breadcrumb from "@/components/Breadcrumbs/Breadcrumb";
import DefaultLayout from "@/components/Layouts/DefaultLayout";
import { AuthActions } from "@/app/auth/utils";
import { YoutubeDLActions } from "@/app/download/utils";
import { useRouter } from "next/navigation";
import { toast } from "react-toastify";
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faDownload } from '@fortawesome/free-solid-svg-icons';
import Loader from "@/components/common/Loader";

type FormData = {
  url: string;
};

const Download: React.FC = () => {
  const router = useRouter();
  const { login, storeToken, loggedIn } = AuthActions();
  const { download } = YoutubeDLActions();
  const {
    register,
    handleSubmit,
    formState: { errors },
    setError,
  } = useForm<FormData>();

  const [isLoading, setIsLoading] = useState(false);
  const [downloadLinks, setDownloadLinks] = useState<string[]>([]);
  const [prevErrors, setPrevErrors] = useState<string[]>([]);

  const urlPattern = /^(https:\/\/(?:www\.youtube\.com\/watch\?v=.+|soundcloud\.com\/.+\/.+))$/;

  const onSubmit = (data: FormData) => {
    setIsLoading(true);
    download(data.url).json((json) => {
      setIsLoading(false);
      if (json.success && json.download) {
        setDownloadLinks(json.download);
        toast.success("Downloaded");
      } else {
        toast.error('Error Downloading');
      }
    })
      .catch((err) => {
        setIsLoading(false);
        console.log(err);
        toast.error('Error Downloading');
      });
  };
  
  return (
    <DefaultLayout>
      <Breadcrumb pageName="Download" />

      <Loader visible={isLoading} />

      <div className="rounded-sm border border-stroke bg-white shadow-default dark:border-strokedark dark:bg-boxdark">
        <div className="flex flex-wrap items-center">
          <div className="w-full border-stroke dark:border-strokedark xl:w-1/1 xl:border-l-2">
            <div className="w-full p-4 sm:p-12.5 xl:p-17.5">
              <form onSubmit={handleSubmit(onSubmit)}>
                <div className="mb-4">
                  <label className="mb-2.5 block font-medium text-black dark:text-white">
                    URL
                  </label>
                  <div className="relative">
                    <input
                      type="text"
                      placeholder="Enter your url"
                      {...register("url", {
                        required: "URL is required",
                        pattern: {
                          value: urlPattern,
                          message: "Incorrect URL format",
                        },
                      })}
                      className="w-full rounded-lg border border-stroke bg-transparent py-4 pl-6 pr-10 text-black outline-none focus:border-primary focus-visible:shadow-none dark:border-form-strokedark dark:bg-form-input dark:text-white dark:focus:border-primary"
                    />
                  </div>
                </div>
                <div className="mb-5">
                  <input
                    type="submit"
                    value="Download"
                    className="w-full cursor-pointer rounded-lg border border-primary bg-primary p-4 text-white transition hover:bg-opacity-90"
                  />
                </div>
              </form>
              {downloadLinks.length > 0 && (
                <div className="mt-6">
                  <h3 className="mb-4 text-lg font-medium text-black dark:text-white">Download Links</h3>
                  <ul>
                    {downloadLinks.map((link, index) => (
                      <li key={index} className="mb-2">
                        <a href={link} download className="text-primary hover:underline flex items-center">
                          <FontAwesomeIcon icon={faDownload} className="mr-2" />
                          {link.split('/').pop()}
                        </a>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </DefaultLayout>
  );
};

export default Download;
