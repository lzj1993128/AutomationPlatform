import request from '@/utils/request'

export function login(data) {
  return request({
    url: '/v1/v1/api/login',
    // url: '/vue-element-admin/user/login',
    method: 'post',
    data: data
  })
}

export function getInfo(token) {
  return request({
    url: '/v1/v1/api/user/info',
    method: 'get',
    params: { token }
  })
}

export function logout() {
  return request({
    url: '/v1/v1/api/logout',
    method: 'post'
  })
}

// export function userSearch(data) {
//   return request({
//     url: '/v1/v1/api/user/search',
//     method: 'post',
//     data: data
//   })
// }
//
// export function userAdd(data) {
//   return request({
//     url: '/v1/v1/api/user/add',
//     method: 'post',
//     data: data
//   })
// }
//
// export function passwordUpdate(data) {
//   return request({
//     url: '/v1/v1/api/user/passwordUpdate',
//     method: 'post',
//     data: data
//   })
// }
