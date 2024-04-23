"use client";

import useSWR from "swr";
import { fetcher } from "@/app/fetcher";
import { useForm } from "react-hook-form";
import { YoutubeDLActions } from "@/app/youtubedl/utils";
import { useRouter } from "next/navigation";
import Link from "next/link";

type FormData = {
  url: string;
};

export default function Home() {
  const router = useRouter();

  const {
    register,
    handleSubmit,
    formState: { errors },
    setError,
  } = useForm<FormData>();

  const { data: playlists } = useSWR("/api/youtubedl?type=playlists", fetcher);
  console.log(playlists)
  const { download } = YoutubeDLActions();

  const onSubmit = (data: FormData) => {
    download(data.url)
    .json((json) => {

      // router.push("dashboard");
    })
    .catch((err) => {
      console.log(err)
      // setError("root", { type: "manual", message: err.json.detail });
    });
  };

  return (
    <div className="flex items-center justify-center min-h-screen bg-gray-100">
      <div className="px-8 py-6 mt-4 text-left bg-white shadow-lg w-1/3">
        <h3 className="text-2xl font-semibold">Download using YouTubeDL</h3>
        <form onSubmit={handleSubmit(onSubmit)} className="mt-4">
          <div>
            <label className="block" htmlFor="url">
              URL
            </label>
            <input
              type="text"
              placeholder="URL"
              {...register("url", { required: true })}
              value="https://soundcloud.com/thekiadoe/ascend"
              className="w-full px-4 py-2 mt-2 border rounded-md focus:outline-none focus:ring-1 focus:ring-blue-600"
            />
            {errors.url && (
              <span className="text-xs text-red-600">Url is required</span>
            )}
          </div>
          <div className="flex items-center justify-between mt-4">
            <button className="px-12 py-2 leading-5 text-white transition-colors duration-200 transform bg-blue-600 rounded-md hover:bg-blue-700 focus:outline-none focus:bg-blue-700">
              Download
            </button>
          </div>
          {errors.root && (
            <span className="text-xs text-red-600">{errors.root.message}</span>
          )}
        </form>
      </div>
    </div>
  );
}
