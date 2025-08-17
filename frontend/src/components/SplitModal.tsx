import React, { useState } from "react";

type Person = {
    id: number;
    name: string;
};

type Transaction = {
    amount_total: number;
    payer_person_id: number;
};

type ShareInput = {
    person_id: number;
    amount: number;
    source: "user_manual";
};

type SplitModalProps = {
    transaction: Transaction;
    people: Person[];
    onSave: (payload: { payer_person_id: number; shares: ShareInput[] }) => void;
    onClose: () => void;
}

export default function SplitModal({ transaction, people, onSave, onClose }: SplitModalProps) {
    const [shares, setShares] = useState<ShareInput[]>(() => 
        people.map((p) => ({ person_id: p.id, amount: 0, source: "user_manual"}))
    );

    const [payer, setPayer] = useState<number>(transaction.payer_person_id);

    const totalAssigned = shares.reduce((sum, s) => sum + s.amount, Number(0));
    const remaining = Number(transaction.amount_total) - totalAssigned;

    const handleAmountChange = (index: number, amount: string) => {
        const newShares = [...shares];
        newShares[index] = { ...newShares[index], amount: parseFloat(amount) || 0 };
        setShares(newShares);
    };
    
    const handleSave = () => {
        if (Math.abs(remaining) > 0.01) {
            alert("The total assigned amount must match the transaction amount.");
            return;
        }
        onSave({ payer_person_id: payer, shares });
        onClose();
    };

    return (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center">
          <div className="bg-white p-4 rounded shadow w-96">
            <h2 className="text-lg font-bold mb-4">Split transaction</h2>
    
            <label className="block mb-2">Payer:</label>
            <select
              className="border p-1 mb-4 w-full"
              value={payer}
              onChange={(e: React.ChangeEvent<HTMLSelectElement>) =>
                setPayer(Number(e.target.value))
              }
            >
              {people.map((p) => (
                <option key={p.id} value={p.id}>
                  {p.name}
                </option>
              ))}
            </select>
    
            {people.map((p, index) => (
              <div key={p.id} className="flex items-center mb-2">
                <span className="w-24">{p.name}</span>
                <input
                  type="number"
                  step="0.01"
                  className="border p-1 flex-1"
                  value={shares[index]?.amount ?? 0}
                  onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
                    handleAmountChange(index, e.target.value)
                  }
                />
              </div>
            ))}
    
            <div className="text-sm text-gray-600 mb-2">
              Remaining: {remaining.toFixed(2)}
            </div>
    
            <div className="flex justify-end space-x-2">
              <button 
                onClick={onClose}
                className="px-3 py-1 border rounded"
                type="button">
                Cancel
              </button>
              <button
                onClick={handleSave}
                className="px-3 py-1 bg-blue-600 text-white rounded"
                type="button"
              >
                Save
              </button>
            </div>
          </div>
        </div>
    );
}