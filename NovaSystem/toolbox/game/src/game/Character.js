class Character {
    constructor(name, className) {
        this.name = name;
        this.className = className;
        this.level = 1;
        this.health = 100;
        this.maxHealth = 100;
        this.strength = 10;
        this.dexterity = 10;
        this.intelligence = 10;
        this.inventory = {};
    }

    levelUp() {
        this.level++;
        this.maxHealth += 10;
        this.health = this.maxHealth;
        this.strength += 2;
        this.dexterity += 2;
        this.intelligence += 2;
    }

    addToInventory(item, quantity = 1) {
        console.log(`Adding to inventory: ${item} (${quantity})`);
        this.inventory[item] = (this.inventory[item] || 0) + quantity;
        console.log('Updated inventory:', this.inventory);
    }

    removeFromInventory(item, quantity = 1) {
        console.log(`Removing from inventory: ${item} (${quantity})`);
        if (this.inventory[item]) {
            this.inventory[item] -= quantity;
            if (this.inventory[item] <= 0) {
                delete this.inventory[item];
            }
            console.log('Updated inventory:', this.inventory);
            return true;
        }
        return false;
    }

    useItem(item) {
        if (this.removeFromInventory(item)) {
            // Define item effects here
            const itemEffects = {
                "Health Potion": () => {
                    this.health = Math.min(this.health + 20, this.maxHealth);
                    return "Restored 20 health.";
                },
                "Strength Potion": () => {
                    this.strength += 5;
                    return "Increased strength by 5.";
                },
                // Add more items and their effects as needed
            };
            
            if (itemEffects[item]) {
                return itemEffects[item]();
            }
        }
        return "Item not found or has no effect.";
    }

    toJSON() {
        return {
            name: this.name,
            className: this.className,
            level: this.level,
            health: this.health,
            maxHealth: this.maxHealth,
            strength: this.strength,
            dexterity: this.dexterity,
            intelligence: this.intelligence,
            inventory: this.inventory
        };
    }

    static fromJSON(json) {
        const character = new Character(json.name, json.className);
        Object.assign(character, json);
        return character;
    }
}

export default Character;