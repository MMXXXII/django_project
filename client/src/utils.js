import { ref } from 'vue'

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

export const dataReloadTrigger = ref(0)

export function triggerDataReload() {
  dataReloadTrigger.value++
}

export function handleApiError(err, fallbackMessage = 'Ошибка', showNotificationCallback) {
  console.error(err);
  const msg = err?.response?.data?.detail || err?.message || fallbackMessage;
  if (showNotificationCallback) {
    showNotificationCallback(msg, 'danger');
  }
}

export async function fetchData(url, notificationCallback) {
    const r = await axios.get(url);
    return r.data;
}

export function clearTimeoutAndHideModal(modalInstance, modalEl) {
  if (modalInstance) modalInstance.hide();
  document.querySelectorAll(".modal-backdrop").forEach(el => el.remove());
}

export function toggleSelection(selectedArray, id) {
  const idx = selectedArray.indexOf(id);
  if (idx >= 0) {
    selectedArray.splice(idx, 1);
  } else {
    selectedArray.push(id);
  }
}


