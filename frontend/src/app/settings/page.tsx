'use client';
import Breadcrumb from "@/components/Breadcrumbs/Breadcrumb";
import Image from "next/image";
import DefaultLayout from "@/components/Layouts/DefaultLayout";

import React, { useState, useEffect } from "react";
import { useForm } from "react-hook-form";
import { useRouter } from "next/navigation";
import { toast } from "react-toastify";
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faDownload, faEnvelope, faPen, faPerson, faTrash } from '@fortawesome/free-solid-svg-icons';
import Loader from "@/components/common/Loader";

import { YoutubeDLActions } from "@/app/download/utils";
import { AuthActions } from "@/app/auth/utils";
const { getToken } = AuthActions();

type FormData = {
  url: string;
  first_name: string
  last_name: string
  email: string
  username: string
  is_superuser: boolean
  is_staff: boolean
};

const Settings = () => {
  const user = getToken('user');

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

  const onSubmitPersonalInfo = (data) => {
    setIsLoading(true);
    updateUser(data)
      .json((json) => {
        setIsLoading(false);
        if (json.success) {
          toast.success("User updated!");
        } else {
          toast.error('Error updating user!');
        }
      })
      .catch((err) => {
        setIsLoading(false);
        console.log(err);
        toast.error('Error updating user!');
      });
  };

  const onSubmitPhoto = (data) => {
    setIsLoading(true);
    // Assuming you have an uploadPhoto function to handle the upload
    uploadPhoto(data.photo[0])
      .json((json) => {
        setIsLoading(false);
        if (json.success) {
          toast.success("Photo uploaded!");
        } else {
          toast.error('Error uploading photo!');
        }
      })
      .catch((err) => {
        setIsLoading(false);
        console.log(err);
        toast.error('Error uploading photo!');
      });
  };

  console.log(user);

  return (
    <DefaultLayout>
      <div className="mx-auto max-w-270">
        <Breadcrumb pageName="Settings" />

        <div className="grid grid-cols-5 gap-8">
          <div className="col-span-5 xl:col-span-3">
            <div className="rounded-sm border border-stroke bg-white shadow-default dark:border-strokedark dark:bg-boxdark">
              <div className="border-b border-stroke px-7 py-4 dark:border-strokedark">
                <h3 className="font-medium text-black dark:text-white">
                  Personal Information
                </h3>
              </div>
              <div className="p-7">
                <form onSubmit={handleSubmit(onSubmitPersonalInfo)}>
                  <div className="mb-5.5 flex flex-col gap-5.5 sm:flex-row">
                    <div className="w-full sm:w-1/2">
                      <label
                        className="mb-3 block text-sm font-medium text-black dark:text-white"
                        htmlFor="firstName"
                      >
                        First Name
                      </label>
                      <div className="relative">
                        <span className="absolute left-4.5 top-3.5">
                          <FontAwesomeIcon icon={faPerson} />
                        </span>
                        <input
                          className="w-full rounded border border-stroke bg-gray py-3 pl-11 pr-4.5 text-black focus:border-primary focus-visible:outline-none dark:border-strokedark dark:bg-meta-4 dark:text-white dark:focus:border-primary"
                          type="text"
                          placeholder="First Name"
                          defaultValue={user.first_name}
                          {...register('first_name')}
                        />
                      </div>
                    </div>

                    <div className="w-full sm:w-1/2">
                      <label
                        className="mb-3 block text-sm font-medium text-black dark:text-white"
                        htmlFor="lastName"
                      >
                        Last Name
                      </label>
                      <div className="relative">
                        <span className="absolute left-4.5 top-3.5">
                          <FontAwesomeIcon icon={faPerson} />
                        </span>
                        <input
                          className="w-full rounded border border-stroke bg-gray py-3 pl-11 pr-4.5 text-black focus:border-primary focus-visible:outline-none dark:border-strokedark dark:bg-meta-4 dark:text-white dark:focus:border-primary"
                          type="text"
                          placeholder="Last Name"
                          defaultValue={user.last_name}
                          {...register('last_name')}
                        />
                      </div>
                    </div>
                  </div>

                  {/* <div className="mb-5.5">
                    <label
                      className="mb-3 block text-sm font-medium text-black dark:text-white"
                      htmlFor="phoneNumber"
                    >
                      Phone Number
                    </label>
                    <input
                      className="w-full rounded border border-stroke bg-gray px-4.5 py-3 text-black focus:border-primary focus-visible:outline-none dark:border-strokedark dark:bg-meta-4 dark:text-white dark:focus:border-primary"
                      type="text"
                      placeholder="Phone Number"
                      {...register('phone-Number')}
                    />
                  </div> */}

                  <div className="mb-5.5">
                    <label
                      className="mb-3 block text-sm font-medium text-black dark:text-white"
                      htmlFor="emailAddress"
                    >
                      Email Address
                    </label>
                    <div className="relative">
                      <span className="absolute left-4.5 top-4">
                        <FontAwesomeIcon icon={faEnvelope} />
                      </span>
                      <input
                        className="w-full rounded border border-stroke bg-gray py-3 pl-11.5 pr-4.5 text-black focus:border-primary focus-visible:outline-none dark:border-strokedark dark:bg-meta-4 dark:text-white dark:focus:border-primary"
                        type="email"
                        placeholder="Email Address"
                        defaultValue={user.email}
                        {...register('email')}
                      />
                    </div>
                  </div>

                  <div className="mb-5.5">
                    <label
                      className="mb-3 block text-sm font-medium text-black dark:text-white"
                      htmlFor="username"
                    >
                      Username
                    </label>
                    <input
                      className="w-full rounded border border-stroke bg-gray px-4.5 py-3 text-black focus:border-primary focus-visible:outline-none dark:border-strokedark dark:bg-meta-4 dark:text-white dark:focus:border-primary"
                      type="text"
                      placeholder="Username"
                      defaultValue={user.username}
                      {...register('username')}
                    />
                  </div>

                  {/* <div className="mb-5.5">
                    <label
                      className="mb-3 block text-sm font-medium text-black dark:text-white"
                      htmlFor="bio"
                    >
                      BIO
                    </label>
                    <div className="relative">
                      <span className="absolute left-4.5 top-4">
                        <FontAwesomeIcon icon={faPen} />
                      </span>

                      <textarea
                        className="w-full rounded border border-stroke bg-gray py-3 pl-11.5 pr-4.5 text-black focus:border-primary focus-visible:outline-none dark:border-strokedark dark:bg-meta-4 dark:text-white dark:focus:border-primary"
                        rows={6}
                        placeholder="Write your bio here"
                        {...register('bio')}
                      ></textarea>
                    </div>
                  </div> */}

                  <div className="mb-5.5 flex flex-col gap-5.5 sm:flex-row">
                    <div className="w-full sm:w-1/1 flex flex-col items-end">
                      <div className="flex items-center mb-3">
                        <label className="block text-sm font-medium text-black dark:text-white mr-2" htmlFor="isSuperuser">
                          Is Superuser
                        </label>
                        <input
                          type="checkbox"
                          className="h-5 w-5 rounded border-stroke bg-gray text-black focus:border-primary focus-visible:outline-none dark:border-strokedark dark:bg-meta-4 dark:text-white dark:focus:border-primary"
                          defaultChecked={user.is_superuser}
                          {...register('is_superuser')}
                        />
                      </div>
                      <div className="flex items-center mb-3">
                        <label className="block text-sm font-medium text-black dark:text-white mr-2" htmlFor="isStaff">
                          Is Staff
                        </label>
                        <input
                          type="checkbox"
                          className="h-5 w-5 rounded border-stroke bg-gray text-black focus:border-primary focus-visible:outline-none dark:border-strokedark dark:bg-meta-4 dark:text-white dark:focus:border-primary"
                          defaultChecked={user.is_staff}
                          {...register('is_staff')}
                        />
                      </div>
                    </div>
                  </div>

                  <div className="flex justify-end gap-4.5">
                    <button
                      className="flex justify-center rounded border border-stroke px-6 py-2 font-medium text-black hover:shadow-1 dark:border-strokedark dark:text-white"
                      type="button"
                      onClick={() => router.back()}
                    >
                      Cancel
                    </button>
                    <button
                      className="flex justify-center rounded bg-primary px-6 py-2 font-medium text-gray hover:bg-opacity-90"
                      type="submit"
                    >
                      Save
                    </button>
                  </div>
                </form>
              </div>
            </div>
          </div>
          <div className="col-span-5 xl:col-span-2">
            <div className="rounded-sm border border-stroke bg-white shadow-default dark:border-strokedark dark:bg-boxdark">
              <div className="border-b border-stroke px-7 py-4 dark:border-strokedark">
                <h3 className="font-medium text-black dark:text-white">
                  Your Photo
                </h3>
              </div>
              <div className="p-7">
                <form onSubmit={handleSubmit(onSubmitPhoto)}>
                  <div className="mb-4 flex items-center gap-3">
                    <div className="h-14 w-14 rounded-full">
                      <Image
                        src={"/images/user/user-03.png"}
                        width={55}
                        height={55}
                        alt="User"
                      />
                    </div>
                    <div>
                      <span className="mb-1.5 text-black dark:text-white">
                        Edit your photo
                      </span>
                      <span className="flex gap-2.5">
                        <button type="button" className="text-sm hover:text-primary">
                          <FontAwesomeIcon icon={faTrash} /> Delete
                        </button>
                        <button type="button" className="text-sm hover:text-primary">
                          <FontAwesomeIcon icon={faPen} /> Update
                        </button>
                      </span>
                    </div>
                  </div>

                  <div
                    id="FileUpload"
                    className="relative mb-5.5 block w-full cursor-pointer appearance-none rounded border border-dashed border-primary bg-gray px-4 py-4 dark:bg-meta-4 sm:py-7.5"
                  >
                    <input
                      type="file"
                      accept="image/*"
                      className="absolute inset-0 z-50 m-0 h-full w-full cursor-pointer p-0 opacity-0 outline-none"
                      {...register('photo')}
                    />
                    <div className="flex flex-col items-center justify-center space-y-3">
                      <span className="flex h-10 w-10 items-center justify-center rounded-full border border-stroke bg-white dark:border-strokedark dark:bg-boxdark">
                        <FontAwesomeIcon icon={faDownload} />
                      </span>
                      <p>
                        <span className="text-primary">Click to upload</span> or
                        drag and drop
                      </p>
                      <p className="mt-1.5">SVG, PNG, JPG or GIF</p>
                      <p>(max, 800 X 800px)</p>
                    </div>
                  </div>

                  <div className="flex justify-end gap-4.5">
                    <button
                      className="flex justify-center rounded border border-stroke px-6 py-2 font-medium text-black hover:shadow-1 dark:border-strokedark dark:text-white"
                      type="button"
                      onClick={() => router.back()}
                    >
                      Cancel
                    </button>
                    <button
                      className="flex justify-center rounded bg-primary px-6 py-2 font-medium text-gray hover:bg-opacity-90"
                      type="submit"
                    >
                      Save
                    </button>
                  </div>
                </form>
              </div>
            </div>
          </div>
        </div>
      </div>
    </DefaultLayout>
  );
};

export default Settings;
