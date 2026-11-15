import API from './axios';

// 1. Connexion de l'utilisateur
export const loginUser = async (email, password) => {
  const formData = new FormData();
  formData.append('username', email);
  formData.append('password', password);

  const response = await API.post('/auth/login', formData);
  
  if (response.data.access_token) {
    localStorage.setItem('token', response.data.access_token);
  }
  
  return response.data;
};

// 2. Récupérer l'utilisateur connecté
export const getCurrentUser = async () => {
  const response = await API.get('/auth/me');
  return response.data;
};

// 3. Déconnexion
export const logoutUser = () => {
  localStorage.removeItem('token');
};