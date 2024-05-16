import 'react-toastify/dist/ReactToastify.css';
import { Flip, ToastContainerProps  } from 'react-toastify';

export const toastOptions: ToastContainerProps  = {
  position: "top-center",
  autoClose: 3000,
  hideProgressBar: true,
  closeOnClick: true,
  pauseOnHover: false,
  draggable: false,
  theme: "colored",
  transition: Flip,
};