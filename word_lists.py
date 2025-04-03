import json

class WordListManager:
    """Manages word lists for the spelling practice application."""

    def __init__(self):
        # Default word lists
        self.word_lists = {
            "Common Misspelled Words": [
                "accommodate", "achieve", "across", "aggressive", "apparently", "appearance", "argument", "assassination", "basically", "beginning",
                "believe", "bizarre", "business", "calendar", "cemetery", "committee", "completely", "conscience", "conscious", "consensus",
                "controversy", "convenience", "correlate", "deceive", "definitely", "dependent", "describe", "desperate", "difference", "dilemma",
                "disappear", "disappoint", "disastrous", "discipline", "embarrass", "environment", "exaggerate", "excellent", "existence", "experience",
                "familiar", "finally", "fluorescent", "foreign", "foreseeable", "forty", "forward", "friend", "further", "glamorous",
                "government", "grammar", "grateful", "guarantee", "harass", "height", "hierarchy", "humorous", "hygiene", "hypocrite",
                "ignorance", "immediate", "independent", "indispensable", "intelligence", "interrupt", "irresistible", "knowledge", "license", "maintenance",
                "maneuver", "mathematics", "millennium", "miniature", "minuscule", "mischievous", "misspell", "necessary", "noticeable", "occasion",
                "occurrence", "parallel", "parliament", "pastime", "perceive", "performance", "permanent", "perseverance", "personal", "personnel",
                "perspective", "persuade", "phenomenon", "possession", "potato", "precede", "preference", "prejudice", "prevalent", "privilege",
                "pronunciation", "publicly", "questionnaire", "receive", "recommend", "reference", "relevant", "religious", "repetition", "restaurant",
                "rhythm", "ridiculous", "sacrilegious", "schedule", "separate", "sergeant", "similar", "sincerely", "specifically", "sufficient",
                "surprise", "technique", "temperature", "temporary", "thorough", "threshold", "tomorrow", "tongue", "truly", "tyranny",
                "unanimous", "unfortunately", "unnecessary", "until", "vacuum", "vegetable", "vehicle", "vicious", "weather", "weird"
            ],
            "Beginner Words": [
                "about", "after", "again", "animal", "answer", "because", "before", "between", "build", "carry", "caught", "children",
                "clothes", "different", "early", "earth", "enough", "every", "example", "father", "favorite", "friend", "great", "house",
                "important", "learn", "little", "money", "morning", "mother", "people", "picture", "place", "plant", "point", "question",
                "school", "sentence", "should", "something", "sometimes", "story", "study", "their", "there", "these", "thing", "think",
                "thought", "through", "together", "under", "water", "where", "which", "world", "would", "write", "young"
            ],
            "Advanced Words": [
                "abbreviate", "aberration", "abhorrent", "absolution", "abstinence", "accentuate", "accessible", "acquiesce", "acquisition", "ambiguous",
                "anachronism", "anathema", "annihilate", "anomalous", "antecedent", "antipathy", "antithesis", "apocryphal", "apprehension", "arbitrary",
                "arcane", "archetype", "articulate", "ascertain", "asperity", "assiduous", "assuage", "astringent", "auspicious", "autonomous",
                "avarice", "belligerent", "benevolent", "capricious", "capitulate", "circumlocution", "circumspect", "clandestine", "cognizant", "commensurate",
                "comprehensive", "concomitant", "condescension", "conflagration", "connoisseur", "conscientious", "consternation", "contiguous", "contrite", "conundrum",
                "convergence", "convivial", "corroborate", "credulous", "deleterious", "demagogue", "denigrate", "derivative", "desultory", "detrimental",
                "diaphanous", "didactic", "diffidence", "dilettante", "discernible", "disinterested", "disparate", "disseminate", "dissonance", "divergent",
                "ebullient", "eccentric", "eclectic", "efficacious", "effrontery", "elicit", "eloquent", "emollient", "empirical", "endemic",
                "enervate", "enigmatic", "ephemeral", "equanimity", "equivocate", "erudite", "esoteric", "euphemism", "exacerbate", "exculpate",
                "exigent", "existential", "expedient", "expunge", "extraneous", "facetious", "fallacious", "fastidious", "fatuous", "felicitous",
                "fervent", "filibuster", "fortuitous", "fractious", "garrulous", "grandiloquent", "gregarious", "hackneyed", "halcyon", "hegemony",
                "heterogeneous", "histrionic", "homogeneous", "hyperbole", "iconoclast", "idiosyncratic", "immutable", "impassive", "impecunious", "imperturbable",
                "impetuous", "implacable", "impunity", "incontrovertible", "indeterminate"
            ],
            "Tech Terms": [
                "algorithm", "application", "architecture", "bandwidth", "binary", "bluetooth", "browser", "cache", "cloud", "code",
                "compile", "cookie", "cpu", "cybersecurity", "database", "debug", "deploy", "digital", "domain", "download",
                "encryption", "ethernet", "firewall", "firmware", "framework", "frontend", "backend", "gigabyte", "gpu", "gui",
                "hardware", "html", "http", "https", "interface", "internet", "ip address", "java", "javascript", "json",
                "kernel", "keyboard", "latency", "linux", "login", "malware", "memory", "metadata", "modem", "monitor",
                "network", "node", "offline", "online", "open-source", "operating system", "packet", "password", "patch", "peripheral",
                "phishing", "pixel", "platform", "plugin", "processor", "protocol", "python", "query", "ram", "ransomware",
                "reboot", "resolution", "router", "saas", "scanner", "screen", "script", "sdk", "search engine", "security",
                "server", "software", "spam", "spreadsheet", "sql", "ssd", "ssl", "storage", "stream", "syntax",
                "system", "terabyte", "thread", "traffic", "ui", "update", "upload", "url", "usb", "user",
                "virtual", "virtualization", "virus", "vpn", "wi-fi", "xml"
            ],
            "CLI Commands & Concepts": [
                "alias", "argument", "bash", "batch", "cat", "cd", "chmod", "chown", "command", "console", "copy", "cp", "curl",
                "directory", "echo", "environment", "execute", "exit", "export", "find", "flag", "grep", "head", "history", "home",
                "kill", "less", "link", "ln", "ls", "man", "mkdir", "more", "move", "mv", "nano", "option", "output", "parameter",
                "path", "pipe", "prompt", "pwd", "redirect", "remove", "return code", "rm", "rmdir", "root", "script", "shell",
                "ssh", "stderr", "stdin", "stdout", "sudo", "switch", "tail", "tar", "terminal", "touch", "variable", "vim",
                "wget", "wildcard", "zsh"
            ],
            "CCNA Networking": [
                "access point", "address", "arp", "asic", "authentication", "autonomous system", "bgp", "broadcast", "cable", "cam table",
                "cdp", "cidr", "cisco", "cli", "collision domain", "configuration", "congestion", "connection", "console port", "convergence",
                "crc", "csma/cd", "default gateway", "dhcp", "dns", "duplex", "dynamic routing", "eigrp", "encapsulation", "etherchannel",
                "ethernet", "extended acl", "fcs", "fiber optic", "firewall", "frame", "ftp", "gateway", "hsrp", "hub", "icmp",
                "interface", "ip", "ipv4", "ipv6", "lan", "layer 2", "layer 3", "link state", "load balancing", "mac address", "mask",
                "multicast", "nat", "network address", "ospf", "packet tracer", "pdu", "ping", "poe", "port security", "ppp", "prefix",
                "private ip", "protocol", "public ip", "qos", "rip", "router", "routing table", "segment", "serial", "server", "smtp",
                "snmp", "spanning tree", "ssh", "standard acl", "static route", "stp", "subnet", "subnetting", "switch", "tcp", "telnet",
                "tftp", "topology", "traceroute", "trunk", "udp", "unicast", "vlan", "vpn", "vtp", "wan", "wildcard mask", "wireless", "wireshark"
            ]
        }

        default_list_name = "Common Misspelled Words"
        available_names = list(self.word_lists.keys())
        if default_list_name in self.word_lists:
            self.active_list_name = default_list_name
        elif available_names:
             self.active_list_name = available_names[0]
        else:
             self.active_list_name = "None"

        self.active_list = self.word_lists.get(self.active_list_name, [])

    def get_available_lists(self):
        """Returns a list of available word list names."""
        return list(self.word_lists.keys())

    def set_active_list(self, list_name):
        """Sets the active word list by name."""
        if list_name in self.word_lists:
            self.active_list_name = list_name
            self.active_list = self.word_lists[list_name]
            return True
        return False

    def get_active_list_name(self):
        """Returns the name of the currently active word list."""
        return self.active_list_name

    def get_active_list(self):
        """Returns the currently active word list (the list of words)."""
        return self.active_list if isinstance(self.active_list, list) else []

    def get_word_count(self):
        """Returns the number of words in the active list."""
        return len(self.get_active_list())

    def add_custom_list(self, list_name, words):
        """Adds or replaces a custom word list."""
        if isinstance(list_name, str) and list_name and isinstance(words, list):
            self.word_lists[list_name] = words
            return True
        return False

    def add_word_to_active_list(self, word):
        """Adds a word to the active list if it doesn't already exist."""
        active_list = self.get_active_list()
        word = str(word).strip() if word else ""
        if word and word not in active_list:
            active_list.append(word)
            self.word_lists[self.active_list_name] = active_list # Ensure main dict is updated
            return True
        return False

    def remove_word_from_active_list(self, word):
        """Removes a word from the active list if it exists."""
        active_list = self.get_active_list()
        if word in active_list:
            active_list.remove(word)
            self.word_lists[self.active_list_name] = active_list # Ensure main dict is updated
            return True
        return False

    def save_to_file(self, filename):
        """Saves all current word lists to a JSON file."""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.word_lists, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error saving word lists to {filename}: {e}")
            return False

    def load_from_file(self, filename):
        """Loads word lists from a JSON file, replacing existing lists."""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                loaded_lists = json.load(f)

            if not isinstance(loaded_lists, dict):
                print(f"Error loading: File {filename} is not a valid dictionary format.")
                return False

            valid_lists = {}
            for name, words in loaded_lists.items():
                if isinstance(name, str) and isinstance(words, list):
                     valid_lists[name] = [str(w) for w in words if isinstance(w, (str, int, float))]
                else:
                     print(f"Warning: Skipping invalid list during load - Key: {name}")

            if not valid_lists:
                 print("Error loading: No valid word lists found in file.")
                 return False

            self.word_lists = valid_lists

            available_names = self.get_available_lists()
            if self.active_list_name not in self.word_lists and available_names:
                self.active_list_name = available_names[0] # Set to first available if old one gone

            self.active_list = self.word_lists.get(self.active_list_name, []) # Update active list content

            return True

        except FileNotFoundError:
            print(f"Error loading: File not found - {filename}")
            return False
        except json.JSONDecodeError:
             print(f"Error loading: File {filename} is not valid JSON.")
             return False
        except Exception as e:
            print(f"Error loading word lists from {filename}: {e}")
            return False
