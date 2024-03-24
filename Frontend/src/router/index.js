import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import CustomizationsView from '../views/CustomizationsView.vue'
import UserView from "../views/UserView.vue"
import ErrorView from "../views/ErrorView.vue"
// import Checkout from '../views/Checkout.vue'; // Adjust the path as necessary
import CheckoutView from '@/views/CheckoutView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: "/",
      name: "home",
      component: HomeView,
    },
    {
      path: "/customizations",
      name: "customizations",
      component: CustomizationsView,
    },
    {
      path: "/user",
      name: "user",
      component: UserView,
    },
    {
      path: "/error",
      name: "error",
      component: ErrorView,
    },
    // {
    //   path: '/checkout',
    //   name: 'Checkout',
    //   component: Checkout,
    // },
    {
      path: "/checkout/:gameId",
      name: "Checkout",
      component: CheckoutView,
    }
  ],
});

export default router

