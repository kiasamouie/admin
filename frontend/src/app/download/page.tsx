'use client';

import React, { useState, useEffect } from "react";
import { useForm, useWatch } from "react-hook-form";
import Link from "next/link";
import Breadcrumb from "@/components/Breadcrumbs/Breadcrumb";
import DefaultLayout from "@/components/Layouts/DefaultLayout";
import { YoutubeDLActions } from "@/app/download/utils";
import { useRouter } from "next/navigation";
import { toast } from "react-toastify";
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faDownload, faPlus, faMinus, faTrash } from '@fortawesome/free-solid-svg-icons';
import Loader from "@/components/common/Loader";

type FormData = {
  url: string;
  timestamps: { start: string, end: string }[];
};

const Download: React.FC = () => {
  const router = useRouter();
  const { download, save_track } = YoutubeDLActions();
  const { register, handleSubmit, formState: { errors }, setValue, watch } = useForm<FormData>({
    defaultValues: {
      url: "",
      timestamps: [],
    }
  });

  const [isLoading, setIsLoading] = useState(false);
  const [downloadLinks, setDownloadLinks] = useState<string[]>([]);

  const urlPattern = /^(https:\/\/(?:www\.youtube\.com\/(?:watch\?v=.+|playlist\?list=.+)|soundcloud\.com\/.+\/(?:sets\/.+|.+)|open\.spotify\.com\/(?:track\/.+|playlist\/.+)))$/;
  const timestampPattern = /^([0-1][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9]$/; // hh:mm:ss format validation

  const onSubmit = (data: FormData) => {
    setIsLoading(true);
    const requestData = {
      ...data,
      timestamps: !!data.timestamps ? data.timestamps : [],
    };

    download(requestData).json((json) => {
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

  const timestamps = watch("timestamps"); // Use watch to track changes in timestamps

  // useEffect to listen for changes in the last "end" timestamp field
  useEffect(() => {
    if (timestamps.length > 0) {
      const mostRecentTimestamp = timestamps[timestamps.length - 1];
  
      if (mostRecentTimestamp.end && mostRecentTimestamp.start) {
        const duplicateIndex = timestamps.findIndex((timestamp, i) =>
          timestamps.some((otherTimestamp, j) =>
            i !== j && timestamp.start === otherTimestamp.start && timestamp.end === otherTimestamp.end
          )
        );
  
        if (duplicateIndex !== -1) {
          toast.error("This timestamp already exists.");
          timestamps[timestamps.length - 1] = { start: "", end: "" }; // Clear most recent values
          setValue("timestamps", timestamps); // Update the form values
        }
      }
    }
  }, [timestamps[timestamps.length - 1]?.end]); // Only run when the most recent 'end' field changes
  

  const addTimestamp = () => {
    // Check if the last timestamp is fully completed
    const lastTimestamp = timestamps[timestamps.length - 1];
    if (!!lastTimestamp && (!lastTimestamp.start || !lastTimestamp.end)) {
      toast.error("Please finish last timestamp.");
      return;
    }
    const newTimestamp = { start: "", end: "" };
    const updatedTimestamps = [...timestamps, newTimestamp];
    setValue("timestamps", updatedTimestamps);
  };

  const removeTimestamp = (index: number) => {
    const updatedTimestamps = timestamps.filter((_, i) => i !== index);
    setValue("timestamps", updatedTimestamps);
  };

  const removeAllTimestamps = () => {
    setValue("timestamps", []);
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
                    {errors.url && <p className="text-red-500">{errors.url.message}</p>}
                  </div>
                </div>

                {timestamps.map((timestamp, index) => (
                  <div key={`timestamp-${index}`} className="flex items-center mb-4 space-x-2">
                    <input
                      type="time"
                      step="1"
                      placeholder="Start time (hh:mm:ss)"
                      {...register(`timestamps.${index}.start`, {
                        required: "Start time is required",
                        pattern: {
                          value: timestampPattern,
                          message: "Incorrect time format (hh:mm:ss)"
                        }
                      })}
                      className="w-full rounded-lg border border-stroke bg-transparent py-4 pl-6 pr-10 text-black outline-none focus:border-primary dark:border-form-strokedark dark:bg-form-input dark:text-white"
                    />
                    <input
                      type="time"
                      step="1"
                      placeholder="End time (hh:mm:ss)"
                      {...register(`timestamps.${index}.end`, {
                        required: "End time is required",
                        pattern: {
                          value: timestampPattern,
                          message: "Incorrect time format (hh:mm:ss)"
                        }
                      })}
                      className="w-full rounded-lg border border-stroke bg-transparent py-4 pl-6 pr-10 text-black outline-none focus:border-primary dark:border-form-strokedark dark:bg-form-input dark:text-white"
                    />
                    <button type="button" onClick={() => removeTimestamp(index)} className="ml-2 text-red-500">
                      <FontAwesomeIcon icon={faMinus} />
                    </button>
                  </div>
                ))}

                <div className="mb-4 flex items-center space-x-4">
                  <button type="button" onClick={addTimestamp} className="text-blue-500">
                    <FontAwesomeIcon icon={faPlus} /> Add Timestamp
                  </button>
                  {timestamps.length > 1 && (
                    <button type="button" onClick={removeAllTimestamps} className="text-red-500">
                      <FontAwesomeIcon icon={faTrash} /> Remove All Timestamps
                    </button>
                  )}
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
                        <a href="#" onClick={() => save_track(link)} className="text-primary hover:underline flex items-center">
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

export default Download
