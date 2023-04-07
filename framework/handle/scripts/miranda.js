const app = {
  readFile(file) {
    return __file.read_file(file);
  },
  writeFile(file, content) {
    __file.write_file(file, content);
  },
  createFile(file) {
    __file.create_file(file);
  },
  appendFile(file, content) {
    __file.append_file(file, content);
  },
  writeBytes(file, bytes) {
    __file.writeBytes(file, bytes);
  },
  aPopup(parent, title, message) {
    __aPopup(parent, title, message);
  },
  cPopup(parent, title, message) {
    __cPopup(parent, title, message);
  },
  iPopup(parent, title, message) {
    __iPopup(parent, title, message);
  },
  qPopup(parent, title, message) {
    __qPopup(parent, title, message);
  },
  wPopup(parent, title, message) {
    __wPopup(parent, title, message);
  },
};
