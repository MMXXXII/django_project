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
  try {
    const r = await axios.get(url);
    return r.data;
  } catch (err) {
    handleApiError(err, 'Не удалось загрузить данные', notificationCallback);
  }
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

export function exportData(url, type = 'excel', showNotificationCallback) {
  axios({
    url: `${url}?type=${type}`,
    method: 'GET',
    responseType: 'blob',
  })
    .then((res) => {
      const url = window.URL.createObjectURL(new Blob([res.data]));
      const link = document.createElement("a");
      link.href = url;
      link.setAttribute("download", type === 'excel' ? "data.xlsx" : "data.docx");
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      showNotificationCallback('Файл сформирован, скачивание началось', 'success');
    })
    .catch((err) => {
      handleApiError(err, 'Ошибка при скачивании файла', showNotificationCallback);
    });
}


