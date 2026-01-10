import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'
import CreateRoom from '../views/CreateRoom.vue'
import JoinRoom from '../views/JoinRoom.vue'
import Room from '../views/Room.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      name: 'Home',
      component: Home
    },
    {
      path: '/create',
      name: 'CreateRoom',
      component: CreateRoom
    },
    {
      path: '/join',
      name: 'JoinRoom',
      component: JoinRoom
    },
    {
      path: '/room/:room_id',
      name: 'Room',
      component: Room
    }
  ]
})

export default router
