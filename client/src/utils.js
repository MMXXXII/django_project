import { ref } from 'vue';

export function showNotification(notification, msg, type = "success", duration = 2000) {
  if (notification._timeoutId) {
    clearTimeout(notification._timeoutId);
    notification._timeoutId = null;
  }
  
  notification.message = msg;
  notification.type = type;
  notification.visible = true;

  notification._timeoutId = setTimeout(() => {
    notification.visible = false;
    notification._timeoutId = null;
  }, duration);
}

export const dataReloadTrigger = ref(0);

export function triggerDataReload() {
  dataReloadTrigger.value = dataReloadTrigger.value + 1;
}

export function handleApiError(err, fallbackMessage = 'Ошибка', showNotificationCallback) {
  console.error(err);
  const msg = err?.response?.data?.detail || err?.message || fallbackMessage;
  if (showNotificationCallback) {
    showNotificationCallback(msg, 'danger');
  }
}

export async function fetchData(url) {
  const response = await axios.get(url);
  return response.data;
}

export function clearTimeoutAndHideModal(modalInstance) {
  if (modalInstance) {
    modalInstance.hide();
  }
  document.querySelectorAll(".modal-backdrop").forEach(function(el) {
    el.remove();
  });
}

export function toggleSelection(selectedArray, id) {
  const index = selectedArray.indexOf(id);
  if (index >= 0) {
    selectedArray.splice(index, 1);
  } else {
    selectedArray.push(id);
  }
}