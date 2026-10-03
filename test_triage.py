import pipeline
import database

if __name__ == "__main__":
    database.seed_demo_data(force=True)
    results = pipeline.run_batch_triage()
    print(f"Successfully processed {len(results)} tickets!")
    for r in results:
        t_id = r['audit']['ticket_id']
        intent = r['audit']['predicted_intent']
        mode = r['audit']['dispatch_mode']
        cost = r['audit']['cost_inr']
        policy = r['audit']['deterministic_policy_check']
        print(f"[{t_id}] Intent={intent} | Policy={policy} | Mode={mode} | Cost=Rs.{cost}")
