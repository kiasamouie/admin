'use client';
import Breadcrumb from "@/components/Breadcrumbs/Breadcrumb";
import DefaultLayout from "@/components/Layouts/DefaultLayout";
import React, { useState } from "react";
import { useForm } from "react-hook-form";
import { useRouter } from "next/navigation";
import { toast } from "react-toastify";
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faEnvelope, faPerson } from '@fortawesome/free-solid-svg-icons';
import { AuthActions } from "@/app/auth/utils";
import { UserActions } from "@/app/settings/utils";

const Settings = () => {
  const router = useRouter();
  const { getToken, storeToken } = AuthActions();
  const { updateUser } = UserActions();
  const { register, handleSubmit, formState: { errors } } = useForm<FormData>();

  const [isLoading, setIsLoading] = useState(false);
  const user = getToken('user');
  console.log(user);

  const onSubmitPersonalInfo = (data: FormData) => {
    setIsLoading(true);
    updateUser(data)
      .json((user) => {
        setIsLoading(false);
        if (user) {
          storeToken(JSON.stringify(user), "user");
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

  return (
    <DefaultLayout>
      <Breadcrumb pageName="Settings" />
      <div className="mx-auto max-w-12xl p-6"> {/* Adjusted container width */}
        <div className="rounded-sm border border-stroke bg-white shadow-default dark:border-strokedark dark:bg-boxdark">
          <div className="border-b border-stroke px-7 py-4 dark:border-strokedark">
            <h3 className="font-medium text-black dark:text-white">
              Personal Information
            </h3>
          </div>
          <div className="p-10"> {/* Increased padding */}
            <form onSubmit={handleSubmit(onSubmitPersonalInfo)}>
              <div className="mb-6 grid grid-cols-1 gap-6 sm:grid-cols-2"> {/* Changed layout to grid */}
                <div>
                  <label className="mb-2 block text-sm font-medium text-black dark:text-white" htmlFor="firstName">
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

                <div>
                  <label className="mb-2 block text-sm font-medium text-black dark:text-white" htmlFor="lastName">
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

              <div className="mb-6">
                <label className="mb-2 block text-sm font-medium text-black dark:text-white" htmlFor="emailAddress">
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

              {/* <div className="mb-6">
                <label className="mb-2 block text-sm font-medium text-black dark:text-white" htmlFor="username">
                  Username
                </label>
                <input
                  className="w-full rounded border border-stroke bg-gray px-4.5 py-3 text-black focus:border-primary focus-visible:outline-none dark:border-strokedark dark:bg-meta-4 dark:text-white dark:focus:border-primary"
                  type="text"
                  placeholder="Username"
                  defaultValue={user.username}
                  {...register('username')}
                />
              </div> */}

              <div className="mb-6 grid grid-cols-2 gap-6"> {/* Adjusted layout */}
                <div className="flex items-center">
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
                <div className="flex items-center">
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
    </DefaultLayout>
  );
};

export default Settings;
