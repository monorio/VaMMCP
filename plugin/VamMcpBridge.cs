using System;
using System.IO;
using SimpleJSON;
using UnityEngine;

namespace MVRPlugin
{
    // Session plugin: add this under Session Plugins, not on a scene atom.
    // Scene plugins are destroyed when SuperController.Load() runs.
    public class VamMcpBridge : MVRScript
    {
        private const string BridgeFolderName = "vam-mcp";
        private const float PollSeconds = 0.2f;

        private string _vamRoot;
        private string _bridgeDir;
        private string _commandPath;
        private string _resultPath;
        private string _statusPath;
        private string _lastCommandId = "";
        private float _nextPoll;
        private float _nextStatus;
        private bool _enabled = true;
        private JSONStorableBool _enabledStore;
        private JSONStorableString _statusStore;

        public override void Init()
        {
            try
            {
                _vamRoot = Path.GetFullPath(Path.Combine(Application.dataPath, ".."));
                _bridgeDir = Path.Combine(_vamRoot, "Saves", "PluginData", BridgeFolderName);
                Directory.CreateDirectory(_bridgeDir);
                _commandPath = Path.Combine(_bridgeDir, "command.json");
                _resultPath = Path.Combine(_bridgeDir, "result.json");
                _statusPath = Path.Combine(_bridgeDir, "status.json");

                _enabledStore = new JSONStorableBool("enabled", true, OnEnabledChanged);
                RegisterBool(_enabledStore);
                CreateToggle(_enabledStore);

                _statusStore = new JSONStorableString("status", "");
                CreateTextField(_statusStore);

                SetStatus("ready  root=" + _vamRoot);
                SuperController.LogMessage("VamMcpBridge ready. Bridge dir: " + _bridgeDir);
                WriteStatusFile("idle", null);
            }
            catch (Exception e)
            {
                SuperController.LogError("VamMcpBridge.Init: " + e);
            }
        }

        private void OnEnabledChanged(bool val)
        {
            _enabled = val;
            SetStatus(_enabled ? "enabled" : "paused");
        }

        private void Update()
        {
            try
            {
                if (!_enabled)
                {
                    return;
                }

                if (Time.unscaledTime >= _nextStatus)
                {
                    _nextStatus = Time.unscaledTime + 2f;
                    WriteStatusFile("idle", null);
                }

                if (Time.unscaledTime < _nextPoll)
                {
                    return;
                }
                _nextPoll = Time.unscaledTime + PollSeconds;
                PollCommand();
            }
            catch (Exception e)
            {
                SuperController.LogError("VamMcpBridge.Update: " + e);
            }
        }

        private void PollCommand()
        {
            if (!File.Exists(_commandPath))
            {
                return;
            }

            string text;
            try
            {
                text = File.ReadAllText(_commandPath);
            }
            catch
            {
                return;
            }

            if (string.IsNullOrEmpty(text))
            {
                return;
            }

            JSONNode parsed = JSON.Parse(text);
            JSONClass cmd = parsed != null ? parsed.AsObject : null;
            if (cmd == null)
            {
                return;
            }

            string id = cmd["id"] != null ? cmd["id"].Value : "";
            if (string.IsNullOrEmpty(id) || id == _lastCommandId)
            {
                return;
            }

            _lastCommandId = id;
            string op = cmd["op"] != null ? cmd["op"].Value : "";
            SetStatus("running " + op + " id=" + id);
            WriteStatusFile("running", op);

            try
            {
                JSONClass result = Dispatch(cmd);
                result["id"] = id;
                if (result["ok"] == null)
                {
                    result["ok"] = "true";
                }
                WriteJsonAtomic(_resultPath, result.ToString());
                SetStatus("ok " + op + " id=" + id);
            }
            catch (Exception e)
            {
                JSONClass err = new JSONClass();
                err["id"] = id;
                err["ok"] = "false";
                err["op"] = op;
                err["error"] = e.Message;
                WriteJsonAtomic(_resultPath, err.ToString());
                SetStatus("error " + op + ": " + e.Message);
                SuperController.LogError("VamMcpBridge: " + e);
            }
        }

        private JSONClass Dispatch(JSONClass cmd)
        {
            string op = cmd["op"] != null ? cmd["op"].Value : "";
            JSONClass result = new JSONClass();
            result["op"] = op;
            result["ok"] = "true";

            if (op == "ping" || op == "status")
            {
                result["data"] = StatusPayload();
                return result;
            }

            if (op == "list_persons")
            {
                result["data"] = ListPersons();
                return result;
            }

            if (op == "load_scene")
            {
                string path = RequiredPath(cmd);
                bool merge = cmd["merge"] != null && cmd["merge"].AsBool;
                if (merge)
                {
                    SuperController.singleton.LoadMerge(path);
                }
                else
                {
                    SuperController.singleton.Load(path);
                }
                result["data"] = new JSONClass();
                result["data"]["path"] = path;
                result["data"]["merge"] = merge ? "true" : "false";
                return result;
            }

            if (op == "load_look")
            {
                Atom person = RequiredPerson(cmd);
                string path = RequiredPath(cmd);
                RestorePreset(person, path);
                result["data"] = new JSONClass();
                result["data"]["person"] = person.uid;
                result["data"]["path"] = path;
                result["data"]["kind"] = "look";
                return result;
            }

            if (op == "load_clothing")
            {
                Atom person = RequiredPerson(cmd);
                string path = RequiredPath(cmd);
                RestorePreset(person, path);
                result["data"] = new JSONClass();
                result["data"]["person"] = person.uid;
                result["data"]["path"] = path;
                result["data"]["kind"] = "clothing";
                return result;
            }

            throw new Exception("unknown op: " + op);
        }

        private string RequiredPath(JSONClass cmd)
        {
            string path = cmd["path"] != null ? cmd["path"].Value : "";
            if (string.IsNullOrEmpty(path))
            {
                throw new Exception("missing path");
            }
            return path;
        }

        private Atom RequiredPerson(JSONClass cmd)
        {
            string uid = cmd["person"] != null ? cmd["person"].Value : "";
            if (string.IsNullOrEmpty(uid))
            {
                uid = FirstPersonUid();
            }
            if (string.IsNullOrEmpty(uid))
            {
                throw new Exception("no Person atom in the current scene");
            }

            Atom atom = SuperController.singleton.GetAtomByUid(uid);
            if (atom == null)
            {
                throw new Exception("person not found: " + uid);
            }
            if (atom.type != "Person")
            {
                throw new Exception("atom is not a Person: " + uid);
            }
            return atom;
        }

        private string FirstPersonUid()
        {
            foreach (Atom atom in SuperController.singleton.GetAtoms())
            {
                if (atom != null && atom.type == "Person")
                {
                    return atom.uid;
                }
            }
            return "";
        }

        private JSONArray ListPersons()
        {
            JSONArray list = new JSONArray();
            foreach (Atom atom in SuperController.singleton.GetAtoms())
            {
                if (atom == null || atom.type != "Person")
                {
                    continue;
                }
                JSONClass row = new JSONClass();
                row["uid"] = atom.uid;
                row["name"] = atom.name;
                row["on"] = atom.on ? "true" : "false";
                list.Add(row);
            }
            return list;
        }

        private void RestorePreset(Atom atom, string path)
        {
            JSONNode node = SuperController.singleton.LoadJSON(path);
            if (node == null)
            {
                throw new Exception("could not load JSON: " + path);
            }

            JSONClass jc = node.AsObject;
            if (jc == null)
            {
                throw new Exception("preset is not a JSON object: " + path);
            }

            JSONArray storables = jc["storables"] != null ? jc["storables"].AsArray : null;
            if (storables == null)
            {
                throw new Exception("preset has no storables array: " + path);
            }

            int restored = 0;
            for (int i = 0; i < storables.Count; i++)
            {
                JSONClass storableJSON = storables[i] as JSONClass;
                if (storableJSON == null)
                {
                    continue;
                }
                string id = storableJSON["id"] != null ? storableJSON["id"].Value : "";
                if (string.IsNullOrEmpty(id))
                {
                    continue;
                }
                JSONStorable storable = atom.GetStorableByID(id);
                if (storable == null)
                {
                    continue;
                }
                storable.RestoreFromJSON(storableJSON);
                restored++;
            }

            if (restored == 0)
            {
                throw new Exception("no matching storables on " + atom.uid + " for " + path);
            }
        }

        private JSONClass StatusPayload()
        {
            JSONClass data = new JSONClass();
            data["plugin"] = "VamMcpBridge";
            data["version"] = "0.1.0";
            data["vamRoot"] = _vamRoot;
            data["bridgeDir"] = _bridgeDir;
            data["enabled"] = _enabled ? "true" : "false";
            data["personCount"] = ListPersons().Count.ToString();
            return data;
        }

        private void WriteStatusFile(string state, string op)
        {
            try
            {
                JSONClass status = StatusPayload();
                status["state"] = state;
                if (!string.IsNullOrEmpty(op))
                {
                    status["op"] = op;
                }
                status["updatedAt"] = DateTime.UtcNow.ToString("o");
                WriteJsonAtomic(_statusPath, status.ToString());
            }
            catch
            {
            }
        }

        private void WriteJsonAtomic(string path, string json)
        {
            string tmp = path + ".tmp";
            File.WriteAllText(tmp, json);
            if (File.Exists(path))
            {
                File.Delete(path);
            }
            File.Move(tmp, path);
        }

        private void SetStatus(string text)
        {
            if (_statusStore != null)
            {
                _statusStore.val = DateTime.Now.ToString("HH:mm:ss") + "  " + text;
            }
        }

        private void OnDestroy()
        {
            try
            {
                WriteStatusFile("stopped", null);
            }
            catch
            {
            }
        }
    }
}
