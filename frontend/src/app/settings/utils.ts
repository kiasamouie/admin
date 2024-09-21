import wretch from "wretch";
import { AuthActions } from "@/app/auth/utils";
const { getToken } = AuthActions();

// Base API setup for making HTTP requests
const baseApi = wretch("http://localhost:8000").accept("application/json");

const api = () => {
  const token = getToken('access');
  return token ? baseApi.auth(`Bearer ${token}`) : baseApi;
};

/**
 * Updates the user information.
 * @param {FormData} user - The updated user data.
 * @returns {Promise} A promise that resolves with the update response.
 */
const updateUser = (user: FormData) => {
  return api().url("/auth/update/").put(user);
};

/**
 * Exports authentication-related actions.
 * @returns {Object} An object containing all the user actions.
 */
export const UserActions = () => {
  return {
    updateUser
  };
};
